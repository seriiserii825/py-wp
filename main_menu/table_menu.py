from rich import print
from rich.markup import escape

from classes.utils.ColorMenu import ColorMenu

# table_menu() result for the Back row
BACK = -1


def table_menu(
    title: str,
    options: list[str],
    back: bool = True,
    red_options: set[str] | None = None,
) -> int:
    """Colored fzf menu (py_libs Menu.select_fzf_menu) with Back / Exit
    rows appended (red). Returns the index of the picked option, BACK for
    Back (or Esc); Exit quits the program. `back=False` — top-level menu,
    only Exit is added and Esc exits too."""
    rows = options + (["Go Back"] if back else [])
    red = (red_options or set()) | {"Back"}
    labels = [
        f"[{'red' if o in red else ('blue' if i % 2 == 0 else 'green')}]{escape(o)}"
        for i, o in enumerate(rows)
    ]
    exit_index = len(rows)
    choice = ColorMenu.select(
        labels, title=title, esc=len(options) if back else exit_index
    )
    if choice == exit_index:
        print("[red]Exiting the program. Goodbye!")
        exit(0)
    if choice >= len(options):
        return BACK
    return choice
