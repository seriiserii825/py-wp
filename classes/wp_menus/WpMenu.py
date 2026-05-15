import shlex

from rich import print
from rich.console import Console
from rich.table import Table

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
            self._add_custom(slug)
        elif choice == 1:
            self._add_post(slug, "post")
        elif choice == 2:
            self._add_post(slug, "page")
        elif choice == 3:
            self._add_term(slug, "category")
        elif choice == 4:
            self._add_post_type_archive(slug)
        elif choice == 5:
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
        options = [f"{i}.{p['post_title']}" for i, p in enumerate(posts)]
        choice = Menu.select_fzf(options)
        if choice == -1:
            return
        Command.run(f"wp menu item add-post {shlex.quote(menu_slug)} {posts[choice]['ID']}")

    def _add_term(self, menu_slug: str, taxonomy: str):
        terms = Command.run_json(
            f"wp term list {taxonomy} --format=json --fields=term_id,name"
        )
        if not terms:
            Print.error(f"No terms in '{taxonomy}'.")
            return
        options = [f"{i}.{t['name']}" for i, t in enumerate(terms)]
        choice = Menu.select_fzf(options)
        if choice == -1:
            return
        Command.run(
            f"wp menu item add-term {shlex.quote(menu_slug)} {taxonomy} {terms[choice]['term_id']}"
        )

    def _add_post_type_archive(self, menu_slug: str):
        post_types = Command.run_json(
            "wp post-type list --format=json --fields=name,label"
        )
        if not post_types:
            Print.error("No post types found.")
            return
        options = [f"{i}.{pt['name']}  ({pt['label']})" for i, pt in enumerate(post_types)]
        choice = Menu.select_fzf(options)
        if choice == -1:
            return
        post_type = post_types[choice]["name"]
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
        options = [f"{i}.{t['name']}  ({t['label']})" for i, t in enumerate(taxonomies)]
        choice = Menu.select_fzf(options)
        if choice == -1:
            return
        self._add_term(menu_slug, taxonomies[choice]["name"])

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

        item_options = [
            f"{i}.{item['title']}  ({item.get('type_label', '')})"
            for i, item in enumerate(items)
        ]
        item_choice = Menu.select_fzf(item_options)
        if item_choice == -1:
            return
        db_id = str(items[item_choice]["db_id"])

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
            self._update_post(db_id, "post")
        elif edit_mode == 3:
            self._update_post(db_id, "page")
        elif edit_mode == 4:
            self._update_term(db_id, "category")
        elif edit_mode == 5:
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
        options = [f"{i}.{p['post_title']}" for i, p in enumerate(posts)]
        choice = Menu.select_fzf(options)
        if choice == -1:
            return
        Command.run(
            f"wp menu item update {db_id} --type=post_type --object-id={posts[choice]['ID']}"
        )

    def _update_term(self, db_id: str, taxonomy: str):
        terms = Command.run_json(
            f"wp term list {taxonomy} --format=json --fields=term_id,name"
        )
        if not terms:
            Print.error(f"No terms in '{taxonomy}'.")
            return
        options = [f"{i}.{t['name']}" for i, t in enumerate(terms)]
        choice = Menu.select_fzf(options)
        if choice == -1:
            return
        Command.run(
            f"wp menu item update {db_id} --type=taxonomy --object-id={terms[choice]['term_id']}"
        )

    def _update_taxonomy_term(self, db_id: str):
        taxonomies = Command.run_json(
            "wp taxonomy list --format=json --fields=name,label"
        )
        if not taxonomies:
            Print.error("No taxonomies found.")
            return
        options = [f"{i}.{t['name']}  ({t['label']})" for i, t in enumerate(taxonomies)]
        choice = Menu.select_fzf(options)
        if choice == -1:
            return
        self._update_term(db_id, taxonomies[choice]["name"])

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
        options = [
            f"{i}.{item['title']}  ({item.get('type_label', '')})"
            for i, item in enumerate(items)
        ]
        choice = Menu.select_fzf(options)
        if choice == -1:
            return
        Command.run(f"wp menu item delete {items[choice]['db_id']}")
