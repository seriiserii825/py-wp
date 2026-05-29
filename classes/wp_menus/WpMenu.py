import shlex

from rich import print

from classes.utils.Command import Command
from classes.utils.Menu import Menu
from classes.utils.Print import Print


class WpMenu:
    def __init__(self, location: str):
        self.location = location

    def _get_menu_slug(self) -> str | None:
        menus = Command.run_json("wp menu list --format=json")
        for menu in menus:
            locations = menu.get("locations") or []
            if isinstance(locations, str):
                locations = [loc.strip() for loc in locations.split(",")]
            if self.location in locations:
                return menu["slug"]
        return None

    def _load_raw(self, slug: str) -> list:
        result = Command.run_json(
            f"wp menu item list {shlex.quote(slug)} --format=json"
            f" --fields=db_id,title,type_label,url,position,menu_item_parent"
        )
        return result if isinstance(result, list) else []

    def _build_flat(self, raw: list) -> list:
        top = sorted(
            [i for i in raw if int(i.get("menu_item_parent", 0)) == 0],
            key=lambda x: int(x.get("position", 0)),
        )
        flat: list = []
        for ti, item in enumerate(top):
            flat.append({**item, "_idx": str(ti)})
            children = sorted(
                [i for i in raw if str(i.get("menu_item_parent")) == str(item["db_id"])],
                key=lambda x: int(x.get("position", 0)),
            )
            for ci, child in enumerate(children):
                flat.append({**child, "_idx": f"{ti}.{ci}"})
        return flat

    def _find(self, flat: list, idx_str: str) -> dict | None:
        return next((i for i in flat if i.get("_idx") == idx_str), None)

    def _ask_index(self, flat: list, prompt: str) -> dict:
        valid = sorted(
            {i["_idx"] for i in flat},
            key=lambda x: [int(p) for p in x.split(".")],
        )
        while True:
            raw = input(prompt).strip()
            item = self._find(flat, raw)
            if item is not None:
                return item
            Print.error(f"Invalid index '{raw}'. Valid: {', '.join(valid)}")

    def _format_item(self, item: dict) -> str:
        idx = item["_idx"]
        indent = "  " if "." in idx else ""
        return (
            f"{indent}{idx:<6} {item['title']:<28}"
            f"  {item.get('type_label', ''):<14}  {item.get('url', '')}"
        )

    def _ask_index_fzf(self, flat: list) -> dict | None:
        opts = [self._format_item(i) for i in flat]
        mapping = dict(zip(opts, flat))
        from classes.utils.Select import Select
        selected = Select.select_fzf_one(opts)
        return mapping.get(selected) if selected else None

    def _ask_indexes_fzf(self, flat: list) -> list:
        opts = [self._format_item(i) for i in flat]
        from classes.utils.Menu import Menu
        indices = Menu.select_fzf_multi(opts)
        return [flat[i] for i in indices]

    def _ask_insert(self, flat: list) -> tuple[int, int]:
        """Ask where to insert; returns (parent_db_id, wp_position 1-based)."""
        top_count = sum(1 for i in flat if "." not in i["_idx"])
        while True:
            raw = input("  Insert at index (e.g. 3 or 3.1): ").strip()
            result = self._parse_insert(flat, raw, top_count)
            if result is not None:
                return result
            Print.error(
                f"Invalid position '{raw}'. "
                f"Top level: 0-{top_count}, nested: N.M (parent must exist)."
            )

    def _parse_insert(self, flat: list, idx_str: str, top_count: int) -> tuple[int, int] | None:
        parts = idx_str.split(".")
        try:
            if len(parts) == 1:
                n = int(parts[0])
                if 0 <= n <= top_count:
                    return (0, n + 1)
            elif len(parts) == 2:
                p, c = int(parts[0]), int(parts[1])
                parent = self._find(flat, str(p))
                if parent is not None:
                    child_count = sum(1 for i in flat if i["_idx"].startswith(f"{p}."))
                    if 0 <= c <= child_count:
                        return (int(parent["db_id"]), c + 1)
        except (ValueError, TypeError):
            pass
        return None

    # ------------------------------------------------------------------ display

    def list_items(self) -> list:
        slug = self._get_menu_slug()
        if not slug:
            Print.error(f"No menu assigned to location '{self.location}'.")
            return []
        flat = self._build_flat(self._load_raw(slug))
        print(f"[bold]=== Menu: {slug}  (location: {self.location}) ===[/bold]")
        if not flat:
            print("  [dim](no items)[/dim]")
            return []
        for item in flat:
            idx = item["_idx"]
            if "." in idx:
                display = idx.split(".")[1]
                indent = "  "
            else:
                display = idx
                indent = ""
            print(
                f"[green]{indent}{display} {item['title']}[/green]"
                f" - [blue]{item.get('type_label', '')}[/blue]"
                f" - [cyan]{item.get('url', '')}[/cyan]"
            )
        return flat

    # ------------------------------------------------------------------ assign

    def create_and_assign(self):
        menus = Command.run_json("wp menu list --format=json")
        options = ["0.+ Create new menu"] + [
            f"{i + 1}.{m['slug']}  ({m['name']})" for i, m in enumerate(menus)
        ]
        choice = Menu.select_fzf(options)
        if choice == -1:
            return False

        if choice == 0:
            name = input("  Menu name: ").strip()
            if not name:
                Print.error("Name cannot be empty.")
                return False
            try:
                Command.run_quiet(f"wp menu create {shlex.quote(name)}")
            except RuntimeError as e:
                Print.error(str(e))
                return False
            menus = Command.run_json("wp menu list --format=json")
            slug = next(
                (m["slug"] for m in menus if m["name"] == name),
                name.lower().replace(" ", "-"),
            )
        else:
            slug = menus[choice - 1]["slug"]

        Command.run(f"wp menu location assign {shlex.quote(slug)} {shlex.quote(self.location)}")
        Print.success(f"Menu '{slug}' assigned to '{self.location}'.")
        return True

    # ------------------------------------------------------------------ create

    def create_item(self, flat: list):
        slug = self._get_menu_slug()
        if not slug:
            Print.error(f"No menu assigned to location '{self.location}'.")
            return

        parent_id, position = self._ask_insert(flat)

        choice = Menu.select_fzf([
            "0.Custom link",
            "1.Post",
            "2.Page",
            "3.Category",
            "4.Post type archive",
            "5.Taxonomy term",
        ])
        if choice == -1:
            return

        if choice == 0:
            self._add_custom(slug, position, parent_id)
        elif choice == 1:
            self._add_post(slug, "post", position, parent_id)
        elif choice == 2:
            self._add_post(slug, "page", position, parent_id)
        elif choice == 3:
            self._add_term(slug, "category", position, parent_id)
        elif choice == 4:
            self._add_post_type_archive(slug, position, parent_id)
        elif choice == 5:
            self._add_taxonomy_term(slug, position, parent_id)

    def _pos_args(self, position: int, parent_id: int) -> str:
        s = f" --position={position}"
        if parent_id:
            s += f" --parent-id={parent_id}"
        return s

    def _add_custom(self, menu_slug: str, position: int, parent_id: int):
        url = input("  URL/slug (e.g. /about): ").strip()
        label = input("  Label: ").strip()
        if not url or not label:
            Print.error("URL and label are required.")
            return
        Command.run(
            f"wp menu item add-custom {shlex.quote(menu_slug)} "
            f"{shlex.quote(label)} {shlex.quote(url)}"
            + self._pos_args(position, parent_id)
        )

    def _add_post(self, menu_slug: str, post_type: str, position: int, parent_id: int):
        posts = Command.run_json(
            f"wp post list --post_type={post_type} --format=json --fields=ID,post_title"
        )
        if not posts:
            Print.error(f"No {post_type}s found.")
            return
        indices = Menu.select_fzf_multi([f"{i}.{p['post_title']}" for i, p in enumerate(posts)])
        if not indices:
            return
        for offset, idx in enumerate(indices):
            Command.run(
                f"wp menu item add-post {shlex.quote(menu_slug)} {posts[idx]['ID']}"
                + self._pos_args(position + offset, parent_id)
            )

    def _add_term(self, menu_slug: str, taxonomy: str, position: int, parent_id: int):
        terms = Command.run_json(
            f"wp term list {taxonomy} --format=json --fields=term_id,name"
        )
        if not terms:
            Print.error(f"No terms in '{taxonomy}'.")
            return
        indices = Menu.select_fzf_multi([f"{i}.{t['name']}" for i, t in enumerate(terms)])
        if not indices:
            return
        for offset, idx in enumerate(indices):
            Command.run(
                f"wp menu item add-term {shlex.quote(menu_slug)} {taxonomy} {terms[idx]['term_id']}"
                + self._pos_args(position + offset, parent_id)
            )

    def _add_post_type_archive(self, menu_slug: str, position: int, parent_id: int):
        post_types = Command.run_json("wp post-type list --format=json --fields=name,label")
        if not post_types:
            Print.error("No post types found.")
            return
        choice = Menu.select_fzf(
            [f"{i}.{pt['name']}  ({pt['label']})" for i, pt in enumerate(post_types)]
        )
        if choice == -1:
            return
        post_type = post_types[choice]["name"]
        label = input(f"  Label [{post_type}]: ").strip() or post_type
        url = input(f"  URL [/{post_type}/]: ").strip() or f"/{post_type}/"
        Command.run(
            f"wp menu item add-custom {shlex.quote(menu_slug)} "
            f"{shlex.quote(label)} {shlex.quote(url)}"
            + self._pos_args(position, parent_id)
        )

    def _add_taxonomy_term(self, menu_slug: str, position: int, parent_id: int):
        taxonomies = Command.run_json("wp taxonomy list --format=json --fields=name,label")
        if not taxonomies:
            Print.error("No taxonomies found.")
            return
        choice = Menu.select_fzf(
            [f"{i}.{t['name']}  ({t['label']})" for i, t in enumerate(taxonomies)]
        )
        if choice == -1:
            return
        self._add_term(menu_slug, taxonomies[choice]["name"], position, parent_id)

    # ------------------------------------------------------------------ edit

    def edit_item(self, flat: list):
        if not flat:
            Print.error("No items in this menu.")
            return
        item = self._ask_index_fzf(flat)
        if item is None:
            return
        db_id = str(item["db_id"])
        slug = self._get_menu_slug()
        if slug is None:
            Print.error("Menu slug not found.")
            return
        position = int(item.get("position", 0))
        parent_id = int(item.get("menu_item_parent", 0))

        edit_mode = Menu.select_fzf([
            "0.Edit label / URL",
            "1.Change to Custom link",
            "2.Change to Post",
            "3.Change to Page",
            "4.Change to Category",
            "5.Change to Taxonomy term",
        ])
        if edit_mode == -1:
            return

        if edit_mode == 0:
            self._edit_label_url(db_id)
        elif edit_mode == 1:
            self._update_custom(db_id)
        elif edit_mode == 2:
            self._replace_with_post(slug, db_id, position, parent_id, "post")
        elif edit_mode == 3:
            self._replace_with_post(slug, db_id, position, parent_id, "page")
        elif edit_mode == 4:
            self._replace_with_term(slug, db_id, position, parent_id, "category")
        elif edit_mode == 5:
            self._replace_with_taxonomy_term(slug, db_id, position, parent_id)

    def _edit_label_url(self, db_id: str):
        print("[yellow]Leave blank to keep current value[/yellow]")
        title = input("  Label: ").strip()
        url = input("  URL: ").strip()
        if not title and not url:
            Print.info("Nothing to update.")
            return
        cmd = f"wp menu item update {db_id}"
        if title:
            cmd += f" --title={shlex.quote(title)}"
        if url:
            cmd += f" --url={shlex.quote(url)}"
        Command.run(cmd)

    def _update_custom(self, db_id: str):
        url = input("  URL/slug (e.g. /about): ").strip()
        label = input("  Label: ").strip()
        if not url or not label:
            Print.error("URL and label are required.")
            return
        Command.run(
            f"wp menu item update {db_id} --type=custom"
            f" --url={shlex.quote(url)} --title={shlex.quote(label)}"
        )

    def _replace_with_post(
        self, slug: str, db_id: str, position: int, parent_id: int, post_type: str
    ):
        posts = Command.run_json(
            f"wp post list --post_type={post_type} --format=json --fields=ID,post_title"
        )
        if not posts:
            Print.error(f"No {post_type}s found.")
            return
        choice = Menu.select_fzf([f"{i}.{p['post_title']}" for i, p in enumerate(posts)])
        if choice == -1:
            return
        Command.run_quiet(f"wp menu item delete {db_id}")
        Command.run(
            f"wp menu item add-post {shlex.quote(slug)} {posts[choice]['ID']}"
            + self._pos_args(position, parent_id)
        )

    def _replace_with_term(
        self, slug: str, db_id: str, position: int, parent_id: int, taxonomy: str
    ):
        terms = Command.run_json(
            f"wp term list {taxonomy} --format=json --fields=term_id,name"
        )
        if not terms:
            Print.error(f"No terms in '{taxonomy}'.")
            return
        choice = Menu.select_fzf([f"{i}.{t['name']}" for i, t in enumerate(terms)])
        if choice == -1:
            return
        Command.run_quiet(f"wp menu item delete {db_id}")
        Command.run(
            f"wp menu item add-term {shlex.quote(slug)} {taxonomy} {terms[choice]['term_id']}"
            + self._pos_args(position, parent_id)
        )

    def _replace_with_taxonomy_term(
        self, slug: str, db_id: str, position: int, parent_id: int
    ):
        taxonomies = Command.run_json("wp taxonomy list --format=json --fields=name,label")
        if not taxonomies:
            Print.error("No taxonomies found.")
            return
        choice = Menu.select_fzf(
            [f"{i}.{t['name']}  ({t['label']})" for i, t in enumerate(taxonomies)]
        )
        if choice == -1:
            return
        self._replace_with_term(slug, db_id, position, parent_id, taxonomies[choice]["name"])

    # ------------------------------------------------------------------ move

    def move_item(self, flat: list):
        if not flat:
            Print.error("No items in this menu.")
            return
        from_item = self._ask_index_fzf(flat)
        if from_item is None:
            return
        top_count = sum(1 for i in flat if "." not in i["_idx"])
        while True:
            to_str = input("  Move to position (e.g. 3 or 4.1): ").strip()
            to_result = self._parse_insert(flat, to_str, top_count)
            if to_result is not None:
                break
            Print.error(f"Invalid position '{to_str}'. E.g. 3 or 4.1")
        parent_id, position = to_result
        db_id = str(from_item["db_id"])
        cmd = f"wp menu item update {db_id} --position={position}"
        cmd += f" --parent-id={parent_id}" if parent_id else " --parent-id=0"
        Command.run(cmd)

    # ------------------------------------------------------------------ delete

    def delete_item(self, flat: list):
        if not flat:
            Print.error("No items in this menu.")
            return
        items = self._ask_indexes_fzf(flat)
        if not items:
            return
        for item in items:
            Command.run(f"wp menu item delete {item['db_id']}")
