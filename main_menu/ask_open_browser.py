from typing import Callable

from py_libs.Menu import Menu
from py_libs.Notification import Notification


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


def run_browser_flow(run: Callable[[bool], object], headless: bool) -> None:
    """Run a Playwright flow (`run(headless)`). If the login page has Cloudflare
    Turnstile, tell the user to deactivate the Turnstile plugin and exit —
    an automated browser can't pass it (the flow's browser is already closed)."""
    # imported here: importing WPPlaywright configures logging for the whole process
    from classes.selenium.WPPlaywright import TurnstileBlockedError, log

    try:
        run(headless)
    except TurnstileBlockedError as e:
        log.error(str(e))
        Notification(title="Turnstile blocks the login", message=str(e)).notify()
        raise SystemExit(1)
