import re

from rich import print
from rich.table import Table
from rich.console import Console

from classes.utils.Print import Print
from classes.utils.Select import Select
from classes.utils.WPPaths import WPPaths


class WpMenuLocations:
    def __init__(self):
        self.setup_file_path = WPPaths.get_theme_path() / "inc" / "nav-menu.php"

    def _read(self) -> str:
        return self.setup_file_path.read_text(encoding="utf-8")

    def _write(self, content: str):
        self.setup_file_path.write_text(content, encoding="utf-8")

    def _parse_locations(self) -> list[tuple[str, str]]:
        content = self._read()
        block_match = re.search(
            r"register_nav_menus\(\s*array\((.*?)\)\s*\);",
            content,
            re.DOTALL,
        )
        if not block_match:
            return []
        block = block_match.group(1)
        return re.findall(r"'([\w-]+)'\s*=>\s*esc_html__\('([^']+)'", block)

    def _get_textdomain(self) -> str:
        match = re.search(r"esc_html__\('[^']+',\s*'([^']+)'\)", self._read())
        return match.group(1) if match else "bs-vite"

    def list_locations(self):
        locations = self._parse_locations()
        if not locations:
            print("[red]No menu locations found in ar-setup.php[/red]")
            return
        table = Table(title="Menu Locations", show_lines=True)
        table.add_column("#", style="cyan", width=4)
        table.add_column("Slug", style="yellow")
        table.add_column("Label", style="green")
        for i, (slug, label) in enumerate(locations):
            table.add_row(str(i), slug, label)
        Console().print(table)

    def create_location(self):
        slug = input("Slug (e.g. footer-menu): ").strip()
        if not slug:
            Print.error("Slug cannot be empty.")
            return
        label = input("Label (e.g. Footer Menu): ").strip()
        if not label:
            Print.error("Label cannot be empty.")
            return

        content = self._read()
        if f"'{slug}'" in content:
            Print.error(f"Location '{slug}' already exists.")
            return

        new_entry = f"        '{slug}' => esc_html__('{label}', '{self._get_textdomain()}'),"
        content = re.sub(
            r"(register_nav_menus\(\s*array\()(.*?)(\s*\)\s*\);)",
            lambda m: m.group(1) + m.group(2).rstrip() +
            f"\n{new_entry}" + m.group(3),
            content,
            flags=re.DOTALL,
        )
        self._write(content)
        Print.success(f"Created '{slug}' => '{label}'.")
        self.list_locations()

    def delete_location(self):
        locations = self._parse_locations()
        if not locations:
            Print.error("No locations to delete.")
            return

        options = [f"{slug}  ({label})" for slug,
                   label in locations] + ["Cancel"]
        choice = Select.select_one(options)
        if choice == "Cancel":
            return

        slug = choice.split("  (")[0]
        content = re.sub(
            r"\n?\s*'" + re.escape(slug) +
            r"'\s*=>\s*esc_html__\('[^']+',\s*'[^']+'\),?",
            "",
            self._read(),
        )
        self._write(content)
        Print.success(f"Deleted location '{slug}'.")
        self.list_locations()

    def edit_location(self):
        locations = self._parse_locations()
        if not locations:
            Print.error("No locations to edit.")
            return

        options = [f"{slug}  ({label})" for slug,
                   label in locations] + ["Cancel"]
        choice = Select.select_one(options)
        if choice == "Cancel":
            return

        old_slug, old_label = locations[options.index(choice)]
        print("[yellow]Leave blank to keep current value[/yellow]")
        new_slug = input(f"  Slug [{old_slug}]: ").strip() or old_slug
        new_label = input(f"  Label [{old_label}]: ").strip() or old_label

        if new_slug == old_slug and new_label == old_label:
            Print.info("Nothing changed.")
            return

        content = re.sub(
            r"'" + re.escape(old_slug) + r"'\s*=>\s*esc_html__\('" +
            re.escape(old_label) + r"',\s*'[^']+'\)",
            f"'{new_slug}' => esc_html__('{new_label}', '{self._get_textdomain()}')",
            self._read(),
        )
        self._write(content)
        Print.success(
            f"Updated: '{old_slug}' -> '{new_slug}', '{old_label}' -> '{new_label}'.")
        self.list_locations()

    def choose_location_slug(self) -> str | None:
        locations = self._parse_locations()
        if not locations:
            Print.error("No locations found in nav-menu.php.")
            return None

        options = [f"{slug}  ({label})" for slug,
                   label in locations] + ["Cancel"]
        choice = Select.select_one(options)
        if choice == "Cancel":
            return None

        return choice.split("  (")[0]
