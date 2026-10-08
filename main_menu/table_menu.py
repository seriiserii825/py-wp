from rich import print

from py_libs.Menu import Menu

# table_menu() result for the Back row
BACK = -1


def table_menu(
    title: str,
    options: list[str],
    back: bool = True,
    red_options: set[str] | None = None,
) -> int:
    """Table menu like the main one with Back / Exit rows appended (red).
    Returns the index of the picked option, BACK for Back; Exit quits the
    program. `back=False` — top-level menu, only Exit is added."""
    rows = options + (["Back"] if back else []) + ["Exit"]
    red = (red_options or set()) | {"Back", "Exit"}
    row_styles = {
        i: "bold red"
        if i >= len(options) or o in red
        else ("bold blue" if i % 2 == 0 else "bold green")
        for i, o in enumerate(rows)
    }
    Menu.display(
        title,
        ["Index", "Option"],
        [[str(i), o] for i, o in enumerate(rows)],
        row_styles=row_styles,
    )
    choice = Menu.choose_option()
    if choice == len(rows) - 1:
        print("[red]Exiting the program. Goodbye!")
        exit(0)
    if choice >= len(options):
        return BACK
    return choice
