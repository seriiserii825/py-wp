import shlex

from rich import print
from rich.console import Console
from rich.table import Table

from classes.utils.Command import Command
from classes.utils.Print import Print
from classes.utils.Select import Select


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

    def create_and_assign(self):
        menus = Command.run_json("wp menu list --format=json")
        options = ["+ Create new menu"] + [f"{m['slug']}  ({m['name']})" for m in menus]
        choice = Select.select_fzf_one(options)
        if not choice:
            return False

        if choice == "+ Create new menu":
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
            slug = choice.split("  (")[0]

        Command.run(f"wp menu location assign {shlex.quote(slug)} {shlex.quote(self.location)}")
        Print.success(f"Menu '{slug}' assigned to '{self.location}'.")
        return True

    def list_items(self):
        slug = self._get_menu_slug()
        if not slug:
            Print.error(f"No menu assigned to location '{self.location}'.")
            return
        items = Command.run_json(
            f"wp menu item list {shlex.quote(slug)} --format=json"
            f" --fields=db_id,title,type_label,url"
        )
        if not items:
            Print.info(f"Menu '{slug}' has no items.")
            return
        table = Table(title=f"Menu: {slug}  (location: {self.location})", show_lines=True)
        table.add_column("#", style="cyan", width=4)
        table.add_column("ID", style="dim", width=6)
        table.add_column("Title", style="yellow")
        table.add_column("Type", style="blue")
        table.add_column("URL", style="green")
        for i, item in enumerate(items):
            table.add_row(
                str(i),
                str(item["db_id"]),
                item["title"],
                item.get("type_label", ""),
                item.get("url", ""),
            )
        Console().print(table)

    def create_item(self):
        slug = self._get_menu_slug()
        if not slug:
            Print.error(f"No menu assigned to location '{self.location}'.")
            return

        choice = Select.select_fzf_one([
            "Custom link",
            "Post",
            "Page",
            "Category",
            "Post type archive",
            "Taxonomy term",
        ])
        if not choice:
            return

        if choice == "Custom link":
            self._add_custom(slug)
        elif choice == "Post":
            self._add_post(slug, "post")
        elif choice == "Page":
            self._add_post(slug, "page")
        elif choice == "Category":
            self._add_term(slug, "category")
        elif choice == "Post type archive":
            self._add_post_type_archive(slug)
        elif choice == "Taxonomy term":
            self._add_taxonomy_term(slug)

    def _add_custom(self, menu_slug: str):
        url = input("  URL/slug (e.g. /about): ").strip()
        label = input("  Label: ").strip()
        if not url or not label:
            Print.error("URL and label are required.")
            return
        Command.run(
            f"wp menu item add-custom {shlex.quote(menu_slug)} "
            f"{shlex.quote(label)} {shlex.quote(url)}"
        )

    def _add_post(self, menu_slug: str, post_type: str):
        posts = Command.run_json(
            f"wp post list --post_type={post_type} --format=json --fields=ID,post_title"
        )
        if not posts:
            Print.error(f"No {post_type}s found.")
            return
        choice = Select.select_fzf_one([f"{p['ID']}  {p['post_title']}" for p in posts])
        if not choice:
            return
        post_id = choice.split("  ")[0]
        Command.run(f"wp menu item add-post {shlex.quote(menu_slug)} {post_id}")

    def _add_term(self, menu_slug: str, taxonomy: str):
        terms = Command.run_json(
            f"wp term list {taxonomy} --format=json --fields=term_id,name"
        )
        if not terms:
            Print.error(f"No terms in '{taxonomy}'.")
            return
        choice = Select.select_fzf_one([f"{t['term_id']}  {t['name']}" for t in terms])
        if not choice:
            return
        term_id = choice.split("  ")[0]
        Command.run(f"wp menu item add-term {shlex.quote(menu_slug)} {taxonomy} {term_id}")

    def _add_post_type_archive(self, menu_slug: str):
        post_types = Command.run_json(
            "wp post-type list --format=json --fields=name,label"
        )
        if not post_types:
            Print.error("No post types found.")
            return
        choice = Select.select_fzf_one([f"{pt['name']}  ({pt['label']})" for pt in post_types])
        if not choice:
            return
        post_type = choice.split("  (")[0]
        label = input(f"  Label [{post_type}]: ").strip() or post_type
        url = input(f"  URL [/{post_type}/]: ").strip() or f"/{post_type}/"
        Command.run(
            f"wp menu item add-custom {shlex.quote(menu_slug)} "
            f"{shlex.quote(label)} {shlex.quote(url)}"
        )

    def _add_taxonomy_term(self, menu_slug: str):
        taxonomies = Command.run_json(
            "wp taxonomy list --format=json --fields=name,label"
        )
        if not taxonomies:
            Print.error("No taxonomies found.")
            return
        choice = Select.select_fzf_one([f"{t['name']}  ({t['label']})" for t in taxonomies])
        if not choice:
            return
        self._add_term(menu_slug, choice.split("  (")[0])

    def edit_item(self):
        slug = self._get_menu_slug()
        if not slug:
            Print.error(f"No menu assigned to location '{self.location}'.")
            return
        items = Command.run_json(
            f"wp menu item list {shlex.quote(slug)} --format=json"
            f" --fields=db_id,title,type_label,url"
        )
        if not items:
            Print.error("No items in this menu.")
            return

        item_choice = Select.select_fzf_one([
            f"{item['db_id']}  {item['title']}  ({item.get('type_label', '')})"
            for item in items
        ])
        if not item_choice:
            return
        db_id = item_choice.split("  ")[0]

        edit_mode = Select.select_fzf_one([
            "Edit label / URL",
            "Change to Custom link",
            "Change to Post",
            "Change to Page",
            "Change to Category",
            "Change to Taxonomy term",
        ])
        if not edit_mode:
            return

        if edit_mode == "Edit label / URL":
            self._edit_label_url(db_id)
        elif edit_mode == "Change to Custom link":
            self._update_custom(db_id)
        elif edit_mode == "Change to Post":
            self._update_post(db_id, "post")
        elif edit_mode == "Change to Page":
            self._update_post(db_id, "page")
        elif edit_mode == "Change to Category":
            self._update_term(db_id, "category")
        elif edit_mode == "Change to Taxonomy term":
            self._update_taxonomy_term(db_id)

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

    def _update_post(self, db_id: str, post_type: str):
        posts = Command.run_json(
            f"wp post list --post_type={post_type} --format=json --fields=ID,post_title"
        )
        if not posts:
            Print.error(f"No {post_type}s found.")
            return
        choice = Select.select_fzf_one([f"{p['ID']}  {p['post_title']}" for p in posts])
        if not choice:
            return
        post_id = choice.split("  ")[0]
        Command.run(f"wp menu item update {db_id} --type=post_type --object-id={post_id}")

    def _update_term(self, db_id: str, taxonomy: str):
        terms = Command.run_json(
            f"wp term list {taxonomy} --format=json --fields=term_id,name"
        )
        if not terms:
            Print.error(f"No terms in '{taxonomy}'.")
            return
        choice = Select.select_fzf_one([f"{t['term_id']}  {t['name']}" for t in terms])
        if not choice:
            return
        term_id = choice.split("  ")[0]
        Command.run(f"wp menu item update {db_id} --type=taxonomy --object-id={term_id}")

    def _update_taxonomy_term(self, db_id: str):
        taxonomies = Command.run_json(
            "wp taxonomy list --format=json --fields=name,label"
        )
        if not taxonomies:
            Print.error("No taxonomies found.")
            return
        choice = Select.select_fzf_one([f"{t['name']}  ({t['label']})" for t in taxonomies])
        if not choice:
            return
        self._update_term(db_id, choice.split("  (")[0])

    def move_item(self):
        slug = self._get_menu_slug()
        if not slug:
            Print.error(f"No menu assigned to location '{self.location}'.")
            return
        items = Command.run_json(
            f"wp menu item list {shlex.quote(slug)} --format=json"
            f" --fields=db_id,title,type_label,url"
        )
        if not items:
            Print.error("No items in this menu.")
            return

        self.list_items()
        raw = input("  Move from,to (e.g. 2,4): ").strip()
        try:
            from_idx, to_idx = [int(x.strip()) for x in raw.split(",")]
        except ValueError:
            Print.error("Invalid format. Use: from,to (e.g. 2,4)")
            return

        if not (0 <= from_idx < len(items)) or not (0 <= to_idx < len(items)):
            Print.error(f"Index out of range (0–{len(items) - 1}).")
            return

        if from_idx == to_idx:
            Print.info("Same position, nothing to do.")
            return

        reordered = items[:]
        item = reordered.pop(from_idx)
        reordered.insert(to_idx, item)

        for pos, entry in enumerate(reordered, start=1):
            Command.run_quiet(f"wp menu item update {entry['db_id']} --position={pos}")

        Print.success(f"Moved item [{from_idx}] '{item['title']}' to index [{to_idx}].")

    def delete_item(self):
        slug = self._get_menu_slug()
        if not slug:
            Print.error(f"No menu assigned to location '{self.location}'.")
            return
        items = Command.run_json(
            f"wp menu item list {shlex.quote(slug)} --format=json"
            f" --fields=db_id,title,type_label,url"
        )
        if not items:
            Print.error("No items in this menu.")
            return
        choice = Select.select_fzf_one([
            f"{item['db_id']}  {item['title']}  ({item.get('type_label', '')})"
            for item in items
        ])
        if not choice:
            return
        db_id = choice.split("  ")[0]
        Command.run(f"wp menu item delete {db_id}")
