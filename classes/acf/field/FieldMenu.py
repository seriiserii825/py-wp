import readline
from pathlib import Path
from typing import cast

from rich import print
from rich.console import Group
from rich.padding import Padding
from rich.panel import Panel
from rich.table import Table

from classes.acf.AcfSnapshotService import AcfSnapshotService
from classes.acf.field.factories.FieldFactory import create_field
from classes.acf.field.FieldDeleter import FieldDeleter
from classes.acf.field.FieldDuplicator import FieldDuplicator
from classes.acf.field.FieldEditor import FieldEditor
from classes.acf.field.FieldMover import FieldMover
from classes.acf.field.FieldRepository import FieldRepository
from classes.acf.field.GroupCopy import GroupCopy
from classes.acf.field.MultipleFieldEditor import MultipleFieldEditor
from classes.acf.field.PredefinedFieldCreator import PredefinedFieldCreator
from py_libs.InputValidator import InputValidator


class FieldMenu:
    def __init__(self, file_path: str):
        self.repo = FieldRepository(file_path)
        self.predefined_creator = PredefinedFieldCreator()
        self.mover = FieldMover()
        self.editor = FieldEditor(self.repo, self.mover)
        self.multi_editor = MultipleFieldEditor(self.mover)
        self.deleter = FieldDeleter(self.repo, self.mover)
        self.duplicator = FieldDuplicator(self.repo, self.mover)
        self.copy_group = GroupCopy(file_path)
        self.last_created_index: list[int] | None = None

    def show_all(self) -> None:
        _, fields = self._load_fields()
        for index, field_data in enumerate(fields):
            field = create_field(field_data)
            if field:
                field.print_field_with_subfields(index=index, indent=0)

    def show_collapsed(self) -> None:
        _, fields = self._load_fields()
        for index, field_data in enumerate(fields):
            field = create_field(field_data)
            if field:
                field.print_field(index=index, indent=0)

    def show_only_tab_group(self, active_index: int = 0) -> None:
        _, fields = self._load_fields()
        for index, field_data in enumerate(fields):
            if field_data.get("type") not in ("tab", "group"):
                continue
            field = create_field(field_data)
            if field:
                if active_index == index:
                    field.print_field_with_subfields(index=index, indent=0)
                else:
                    field.print_field(index=index, indent=0, active=False)

    def select_tab_group_index(self) -> int | None:
        from py_libs.Select import Select

        _, fields = self._load_fields()
        tab_groups = [
            (index, fd)
            for index, fd in enumerate(fields)
            if fd.get("type") in ("tab", "group")
        ]
        if not tab_groups:
            print("No tab/group fields found.")
            return None

        width = len(str(len(fields) - 1))
        options = [
            f"{idx:0{width}d}) {fd.get('label', fd.get('name', '?'))} ({fd.get('type')})"
            for idx, fd in tab_groups
        ]
        selected = Select.select_with_fzf(options)
        if not selected or selected == [""]:
            return None

        pos = options.index(selected[0])
        return tab_groups[pos][0]

    def create_with_group(self) -> None:
        """Predefined fields wrapped in a Tab + Group, appended at the end."""
        data, fields = self._load_fields()
        result = self._ask_predefined_fields(with_group=True)
        if result is None:
            return
        fields.extend(result)
        self.repo.save(data)
        label = result[1]["label"]
        sub_labels = ", ".join(f["label"] for f in result[1]["sub_fields"])
        print(f"Predefined fields created: Tab+Group '{label}' with fields: {sub_labels}")

    def create_field_in_group(self) -> None:
        """Predefined fields (no Tab + Group) inserted at an index inside a group."""
        data, fields = self._load_fields()
        new_fields = self._ask_predefined_fields(with_group=False)
        if new_fields is None:
            return
        dest = self._ask_group_insert_index(fields)
        if dest is None:
            print("Cancelled.")
            return
        parent = self.mover.get_field_container(fields, dest)
        insert_at = dest[-1] if dest[-1] is not None else len(parent)
        for offset, field in enumerate(new_fields):
            self.mover.insert_field_into(parent, insert_at + offset, field)
        self.repo.save(data)
        self.last_created_index = cast(list[int], dest[:-1] + [insert_at + len(new_fields) - 1])
        labels = ", ".join(f["label"] for f in new_fields)
        dest_str = ".".join(str(p) for p in dest[:-1] + [insert_at])
        print(f"Predefined fields created at {dest_str}: {labels}")

    def _ask_predefined_fields(self, with_group: bool) -> list[dict] | None:
        """Show the help and read the predefined line until it is valid.
        None = cancelled ('q') or no type shortcuts."""
        try:
            type_map = self.predefined_creator.load_type_map()
        except ValueError as e:
            print(f"[red]{e}[/red]")
            return None
        if not type_map:
            print(
                f"[red]No type shortcuts found in "
                f"{self.predefined_creator.type_csv_path}.[/red]"
            )
            return None

        self._print_predefined_help(type_map, with_group)

        raw = ""
        while True:
            raw = self._prompt_with_prefill("> ", raw)
            if raw.strip().lower() == "q":
                print("Cancelled.")
                return None
            try:
                if with_group:
                    group_label, specs = self.predefined_creator.parse(raw)
                    return self.predefined_creator.build(group_label, specs)
                return self.predefined_creator.build_fields(
                    self.predefined_creator.parse_fields(raw)
                )
            except ValueError as e:
                print(f"[red]{e}[/red]")

    def _ask_group_insert_index(self, fields: list) -> list[int | None] | None:
        """Ask for an index inside a group/repeater (e.g. 1.0, or 1. to append)
        until it is valid, pre-filled with the index right after the last
        created field. None = cancelled ('q')."""
        raw = self._suggest_next_index(fields) or ""
        while True:
            raw = self._prompt_with_prefill(
                "Insert at index inside a group (e.g. 1.0, 1. = append, 'q' to cancel): ",
                raw,
            ).strip()
            if raw.lower() == "q":
                return None
            try:
                return self._validate_group_insert_index(fields, raw)
            except ValueError as e:
                print(f"[red]{e}[/red]")

    def _validate_group_insert_index(self, fields: list, raw: str) -> list[int | None]:
        try:
            path = self.mover.parse_index_path(raw)
        except ValueError:
            raise ValueError(f"Invalid index '{raw}', use numbers separated by '.' (e.g. 1.0).")
        if len(path) < 2:
            raise ValueError(
                f"Index '{raw}' is not inside a group, use e.g. {raw.rstrip('.')}.0."
            )
        if any(p is None or p < 0 for p in path[:-1]) or (path[-1] is not None and path[-1] < 0):
            raise ValueError(f"Invalid index '{raw}'.")

        container = fields
        for depth, idx in enumerate(path[:-1]):
            assert idx is not None
            prefix = ".".join(str(p) for p in path[: depth + 1])
            if idx >= len(container):
                raise ValueError(f"Field at index '{prefix}' does not exist.")
            field = container[idx]
            if field.get("type") not in ("group", "repeater"):
                raise ValueError(
                    f"Field at index '{prefix}' ('{field.get('label', '')}') is "
                    f"a {field.get('type')}, not a group/repeater."
                )
            container = field.setdefault("sub_fields", [])

        last = path[-1]
        if last is not None and last > len(container):
            raise ValueError(
                f"Index '{raw}' is out of range, the group has {len(container)} "
                f"field(s) (max {len(container)} or use a trailing '.')."
            )
        return path

    def _suggest_next_index(self, fields: list) -> str | None:
        if self.last_created_index is None:
            return None
        try:
            parent = self.mover.get_field_container(fields, self.last_created_index)
            last_field = parent[self.last_created_index[-1]]
        except (IndexError, KeyError):
            return None

        path = list(self.last_created_index)
        if last_field.get("type") in ("group", "repeater"):
            path.append(0)
        else:
            path[-1] += 1
        return ".".join(str(p) for p in path)

    def move_field(self) -> str:
        data, fields = self._load_fields()
        self._check_field_is_empty(fields)
        try:
            input_dest = InputValidator.get_string(
                "Enter source and dest separated by comma, 8,4: ",
                allow_empty=True,
            )
            source, dest = (s.strip() for s in input_dest.split(",")) if input_dest else (None, None)
            if not source:
                source = InputValidator.get_string("Enter source index (e.g. 0.1): ")
            if not dest:
                dest = InputValidator.get_string("Enter destination index (e.g. 0.1): ")
            self.mover.move_field(fields, source, dest)
            self.repo.save(data)
            print("Field moved successfully.")
            return dest
        except Exception as e:
            raise Exception(f"Error moving field: {e}")

    def edit_field(self) -> None:
        data, fields = self._load_fields()
        self._check_field_is_empty(fields)
        self.editor.edit_field(data, fields)

    def edit_multiple_fields(self) -> None:
        from main_menu.table_menu import BACK, table_menu

        data, fields = self._load_fields()
        if not fields:
            print("No fields to edit.")
            return

        attrs = [
            MultipleFieldEditor.LABEL,
            MultipleFieldEditor.WIDTH,
            MultipleFieldEditor.TYPE,
        ]
        choice = table_menu("Edit multiple: attribute", [a.title() for a in attrs])
        if choice == BACK:
            return
        attr = attrs[choice]

        type_map: dict[str, str] = {}
        if attr == MultipleFieldEditor.TYPE:
            try:
                type_map = self.predefined_creator.load_type_map()
            except ValueError as e:
                print(f"[red]{e}[/red]")
                return
            if not type_map:
                print(
                    f"[red]No type shortcuts found in "
                    f"{self.predefined_creator.type_csv_path}.[/red]"
                )
                return

        if attr == MultipleFieldEditor.LABEL:
            print(
                "Insert Field name as string, with spaces "
                "(slug/name will be converted automatically). "
                "E.g. 1.2/My label/2.4/New label ('q' to cancel)"
            )
        elif attr == MultipleFieldEditor.WIDTH:
            print(
                f"Insert number from {MultipleFieldEditor.MIN_WIDTH} "
                f"to {MultipleFieldEditor.MAX_WIDTH}. "
                "E.g. 1.2/30/2.4/50 ('q' to cancel)"
            )
        else:
            print("Insert type from predefined CSV:")
            self._print_type_shortcuts(type_map)
            print("E.g. 1.2/t/2.4/i ('q' to cancel)")

        raw = ""
        changes: list[tuple[str, dict, str]] | None = None
        while changes is None:
            raw = self._prompt_with_prefill("> ", raw)
            if raw.strip().lower() == "q":
                print("Cancelled.")
                return
            try:
                changes = self.multi_editor.parse(raw, attr, fields, type_map)
            except ValueError as e:
                print(f"[red]{e}[/red]")

        for index, field, value in changes:
            old = self.multi_editor.apply(attr, field, value, type_map)
            new_value = type_map[value] if attr == MultipleFieldEditor.TYPE else value
            print(f"  [{index}] {attr}: '{old}' → '{new_value}'")
        self.repo.save(data)
        print(f"[green]Done. {len(changes)} field(s) updated.[/green]")

    @staticmethod
    def _print_predefined_help(type_map: dict[str, str], with_group: bool = True) -> None:
        shortcuts = "   ".join(
            f"[bold cyan]{shortcut}[/bold cyan] [dim]{field_type}[/dim]"
            for shortcut, field_type in type_map.items()
        )

        syntax = Table.grid(padding=(0, 2))
        syntax.add_column(style="bold")
        syntax.add_column()
        if with_group:
            syntax.add_row(
                "Group",
                "[yellow]Info[/yellow]  [dim]first item → Tab + Group with this label[/dim]",
            )
        syntax.add_row(
            "Field",
            "[green]Title[/green]/[cyan]t[/cyan]  "
            "[dim]or with width:[/dim] [green]Title[/green]/[cyan]t[/cyan]/[magenta]40[/magenta]"
            "  [dim](default 100)[/dim]",
        )
        syntax.add_row(
            "Repeater",
            "[green]Items[/green][[green]Image[/green]/[cyan]i[/cyan]/"
            "[green]Subtitle[/green]/[cyan]t[/cyan]]  [dim]or with width:[/dim] "
            "[green]Items[/green][…]/[magenta]50[/magenta]",
        )
        syntax.add_row("Types", shortcuts)

        example = (
            ("[yellow]Info[/yellow]/" if with_group else "")
            + "[green]Title[/green]/[cyan]t[/cyan]/[magenta]40[/magenta]/"
            "[green]Description[/green]/[cyan]ta[/cyan]/[magenta]60[/magenta]/"
            "[green]Items[/green][[green]Image[/green]/[cyan]i[/cyan]/[magenta]30[/magenta]/"
            "[green]Subtitle[/green]/[cyan]t[/cyan]]"
        )
        result = Table.grid(padding=(0, 1))
        result.add_column()
        if with_group:
            result.add_row("[yellow]Info[/yellow] [dim](tab + group)[/dim]")
            result.add_row(" ├─ [green]Title[/green] [dim]text, 40%[/dim]")
            result.add_row(" ├─ [green]Description[/green] [dim]textarea, 60%[/dim]")
            result.add_row(" └─ [green]Items[/green] [dim]repeater, 100%[/dim]")
            result.add_row("     ├─ [green]Image[/green] [dim]image, 30%[/dim]")
            result.add_row("     └─ [green]Subtitle[/green] [dim]text, 100%[/dim]")
        else:
            result.add_row("[green]Title[/green] [dim]text, 40%[/dim]")
            result.add_row("[green]Description[/green] [dim]textarea, 60%[/dim]")
            result.add_row("[green]Items[/green] [dim]repeater, 100%[/dim]")
            result.add_row(" ├─ [green]Image[/green] [dim]image, 30%[/dim]")
            result.add_row(" └─ [green]Subtitle[/green] [dim]text, 100%[/dim]")
            result.add_row("[dim]→ then asked for the index inside a group[/dim]")

        body = Group(
            "[dim]Everything is separated by[/dim] [bold]/[/bold][dim]. "
            "Labels may contain spaces — names are generated automatically.[/dim]",
            "",
            syntax,
            "",
            "[bold]Example[/bold]",
            f"  {example}",
            "",
            Padding(result, (0, 0, 0, 2)),
            "",
            "[dim]Enter the line below ·[/dim] [bold red]q[/bold red] [dim]to cancel[/dim]",
        )
        title = "Create with group" if with_group else "Create field in group"
        print(Panel(body, title=f"[bold]{title}[/bold]",
                    title_align="left", border_style="blue", expand=False))

    @staticmethod
    def _print_type_shortcuts(type_map: dict[str, str]) -> None:
        for shortcut, field_type in type_map.items():
            if field_type == "text":
                color = "blue"
            elif field_type == "image":
                color = "green"
            else:
                color = "yellow"
            print(f"  {shortcut} [{color}]({field_type})[/{color}]")

    def delete_field(self) -> None:
        data, fields = self._load_fields()
        self._check_field_is_empty(fields)
        self.deleter.delete_single(data, fields)

    def delete_fields(self) -> None:
        data, fields = self._load_fields()
        self._check_field_is_empty(fields)
        self.deleter.delete_multiple(data, fields)

    def duplicate_field(self) -> None:
        data, fields = self._load_fields()
        self._check_field_is_empty(fields)
        try:
            final_path = self.duplicator.duplicate_field(data, fields)
            if final_path is not None:
                self.last_created_index = final_path
        except Exception as e:
            print(f"Error duplicating field: {e}")

    def move_multiple_fields(self) -> None:
        data, fields = self._load_fields()
        self._check_field_is_empty(fields)
        try:
            raw = InputValidator.get_string("Enter sources|destination (e.g. 2,3,4,5|10 or 2.1,2.3|2.9): ")
            if "|" not in raw:
                print("Invalid format. Use: sources|destination (e.g. 2,3,4|10)")
                return
            sources_part, dest_str = raw.split("|", 1)
            index_strs = [s.strip() for s in sources_part.split(",") if s.strip()]
            dest_str = dest_str.strip()
            if not index_strs or not dest_str:
                print("No indexes provided.")
                return

            source_paths = [self.mover.parse_index_path(s) for s in index_strs]
            dest_path = self.mover.parse_index_path(dest_str)

            # Capture dest parent reference BEFORE any removal so nested navigation stays valid
            dest_parent = self.mover.get_field_container(fields, dest_path, create=True)
            dest_idx = dest_path[-1] if dest_path[-1] is not None else len(dest_parent)

            # Pop in descending order to keep indexes stable; preserve user order via enumerate
            indexed = sorted(enumerate(source_paths), key=lambda x: x[1], reverse=True)
            popped: list[tuple[int, dict]] = []
            for user_idx, path in indexed:
                popped.append((user_idx, self.mover.pop_field(fields, path)))

            # Restore user-selection order
            popped.sort(key=lambda x: x[0])

            # Shift dest index for each source removed from the same parent before it
            dest_parent_path = dest_path[:-1]
            removals_before = sum(
                1 for sp in source_paths
                if sp[:-1] == dest_parent_path and sp[-1] is not None and sp[-1] < dest_idx
            )
            adjusted = dest_idx - removals_before

            for offset, (_, field_data) in enumerate(popped):
                self.mover.insert_field_into(dest_parent, adjusted + offset, field_data)
                print(f"  [{index_strs[offset]}] '{field_data.get('label', '')}' → {adjusted + offset}")

            self.repo.save(data)
            print(f"Done. {len(popped)} field(s) moved.")
        except Exception as e:
            print(f"Error moving fields: {e}")

    def toggle_required(self) -> None:
        data, fields = self._load_fields()
        self._check_field_is_empty(fields)
        try:
            raw = InputValidator.get_string("Enter field indexes separated by comma (e.g. 0,1.2,3): ")
            indexes = [s.strip() for s in raw.split(",") if s.strip()]
            for idx in indexes:
                field = self.mover.get_field_by_index(fields, idx)
                field["required"] = 0 if field.get("required") else True
                state = "required" if field["required"] else "optional"
                print(f"  [{idx}] '{field.get('label', '')}' → {state}")
            self.repo.save(data)
            print("Done.")
        except Exception as e:
            print(f"Error toggling required: {e}")

    def reorder_fields(self) -> None:
        data, fields = self._load_fields()
        self._check_field_is_empty(fields)
        total = len(fields)
        print(f"\nCurrent fields ({total} total):")
        for index, field_data in enumerate(fields):
            field = create_field(field_data)
            if field:
                field.print_field(index=index, indent=0)

        while True:
            try:
                raw = InputValidator.get_string(
                    f"Enter new order (e.g. 3,2,6,1,...) or 'q' to cancel: "
                ).strip()
                if raw.lower() == "q":
                    print("Reorder cancelled.")
                    return

                parts = [p.strip() for p in raw.split(",")]
                indices = [int(p) for p in parts]

                if len(indices) != total:
                    print(
                        f"[red]Error: expected {total} indices, got {len(indices)}. "
                        "Try again or enter 'q' to cancel.[/red]"
                    )
                    continue

                if sorted(indices) != list(range(total)):
                    print(
                        f"[red]Error: indices must be a permutation of 0..{total - 1} "
                        "with no duplicates or out-of-range values. "
                        "Try again or enter 'q' to cancel.[/red]"
                    )
                    continue

                data[0]["fields"] = [fields[i] for i in indices]
                self.repo.save(data)
                print("[green]Fields reordered successfully.[/green]")
                return

            except ValueError:
                print("[red]Error: invalid input — use comma-separated integers. "
                      "Try again or enter 'q' to cancel.[/red]")
            except Exception as e:
                print(f"[red]Unexpected error during reorder: {e}[/red]")
                return

    def reorder_from_snapshot(self, base_dir: Path) -> None:
        AcfSnapshotService.reorder_from_snapshot(Path(self.repo.path), base_dir)
        print("Fields reordered from snapshot.")

    def copy_group_to_clipboard(self) -> None:
        _, fields = self._load_fields()
        self._check_field_is_empty(fields)
        try:
            source = InputValidator.get_string("Enter group index to copy (e.g. 1): ")
            self.copy_group.copy_to_clipboard(fields, source)
            print("Group copied to clipboard.")
        except Exception as e:
            print(f"Error copying group: {e}")

    def _load_fields(self):
        data = self.repo.load()
        return data, data[0].get("fields", [])

    def _check_field_is_empty(self, fields: list):
        if not fields:
            print("No fields to move.")
            return

    @staticmethod
    def _prompt_with_prefill(prompt: str, prefill: str) -> str:
        """input() with the line pre-filled and editable (e.g. re-showing an
        invalid entry so the user can fix it instead of retyping it)."""

        def hook() -> None:
            readline.insert_text(prefill)
            readline.redisplay()

        readline.set_startup_hook(hook)
        try:
            return input(prompt)
        finally:
            readline.set_startup_hook()
