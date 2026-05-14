import re

from rich import print
from rich.table import Table
from rich.console import Console

from classes.utils.WPPaths import WPPaths


class WpMenus:
    def __init__(self):
        self.setup_file_path = WPPaths.get_theme_path() / "inc" / "ar-setup.php"

    def _parse_locations(self) -> list[tuple[str, str]]:
        content = self.setup_file_path.read_text(encoding="utf-8")
        block_match = re.search(
            r"register_nav_menus\(\s*array\((.*?)\)\s*\);",
            content,
            re.DOTALL,
        )
        if not block_match:
            return []
        block = block_match.group(1)
        return re.findall(r"'([\w-]+)'\s*=>\s*esc_html__\('([^']+)'", block)

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
