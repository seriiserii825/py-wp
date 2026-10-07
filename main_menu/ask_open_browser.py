from py_libs.Menu import Menu


def ask_open_browser() -> bool:
    """True → show the browser window, False → run Playwright headless."""
    options = [
        "Yes (show browser)",
        "No (headless)",
    ]
    row_styles = {
        0: "bold blue",
        1: "bold green",
    }
    Menu.display(
        "Open browser?",
        ["Index", "Option"],
        [[str(i), o] for i, o in enumerate(options)],
        row_styles=row_styles,
    )
    return Menu.choose_option() == 0
