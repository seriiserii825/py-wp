from classes.acf.field.factories.FieldFactory import create_field
from classes.acf.field.FieldCreator import FieldCreator
from classes.acf.field.FieldDeleter import FieldDeleter
from classes.acf.field.FieldDuplicator import FieldDuplicator
from classes.acf.field.FieldEditor import FieldEditor
from classes.acf.field.FieldMover import FieldMover
from classes.acf.field.FieldRepository import FieldRepository
from classes.acf.field.GroupCopy import GroupCopy
from classes.utils.InputValidator import InputValidator


class FieldMenu:
    def __init__(self, file_path: str):
        self.repo = FieldRepository(file_path)
        self.creator = FieldCreator()
        self.mover = FieldMover()
        self.editor = FieldEditor(self.repo, self.mover)
        self.deleter = FieldDeleter(self.repo, self.mover)
        self.duplicator = FieldDuplicator(self.repo, self.mover)
        self.copy_group = GroupCopy(file_path)

    def show_all(self):
        _, fields = self._load_fields()
        for index, field_data in enumerate(fields):
            field = create_field(field_data)
            if field:
                field.print_field_with_subfields(index=index, indent=0)

    def show_only_tab_group(self, active_index: int = 0):
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
        from classes.utils.Select import Select

        _, fields = self._load_fields()
        tab_groups = [
            (index, fd)
            for index, fd in enumerate(fields)
            if fd.get("type") in ("tab", "group")
        ]
        if not tab_groups:
            print("No tab/group fields found.")
            return None

        options = [
            f"{idx}) {fd.get('label', fd.get('name', '?'))} ({fd.get('type')})"
            for idx, fd in tab_groups
        ]
        selected = Select.select_with_fzf(options)
        if not selected or selected == [""]:
            return None

        pos = options.index(selected[0])
        return tab_groups[pos][0]

    def create_field(self):
        data, fields = self._load_fields()
        new_field = self.creator.create()
        if isinstance(new_field, list):
            fields.extend(new_field)
        else:
            fields.append(new_field)
        self._move_after_create(fields, data)
        self.repo.save(data)
        print("Field created and saved.")

    def _move_after_create(self, fields: list, data):
        try:
            source_index = str(len(fields) - 1)
            dest = InputValidator.get_string("Enter destination index (e.g. 0.1): ")
            self.mover.move_field(fields, source_index, dest)
            self.repo.save(data)
            print("Field moved successfully.")
        except Exception as e:
            print(f"Error moving newly created field: {e}")

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

    def edit_field(self):
        data, fields = self._load_fields()
        self._check_field_is_empty(fields)
        self.editor.edit_field(data, fields)

    def delete_field(self):
        data, fields = self._load_fields()
        self._check_field_is_empty(fields)
        self.deleter.delete_single(data, fields)

    def delete_fields(self):
        data, fields = self._load_fields()
        self._check_field_is_empty(fields)
        self.deleter.delete_multiple(data, fields)

    def duplicate_field(self):
        data, fields = self._load_fields()
        self._check_field_is_empty(fields)
        try:
            self.duplicator.duplicate_field(data, fields)
        except Exception as e:
            print(f"Error duplicating field: {e}")

    def move_multiple_fields(self):
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
                if sp[:-1] == dest_parent_path and sp[-1] < dest_idx
            )
            adjusted = dest_idx - removals_before

            for offset, (_, field_data) in enumerate(popped):
                self.mover.insert_field_into(dest_parent, adjusted + offset, field_data)
                print(f"  [{index_strs[offset]}] '{field_data.get('label', '')}' → {adjusted + offset}")

            self.repo.save(data)
            print(f"Done. {len(popped)} field(s) moved.")
        except Exception as e:
            print(f"Error moving fields: {e}")

    def toggle_required(self):
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

    def copy_group_to_clipboard(self):
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
