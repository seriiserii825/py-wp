from typing import Callable

from classes.utils.ColorMenu import ColorMenu
from py_libs.Notification import Notification


def ask_open_browser() -> bool | None:
    """True → show the browser window, False → run Playwright headless,
    None → Back (cancel); Exit quits the program."""
    options = [
        "[blue]Yes (show browser)",
        "[green]No (headless)",
        "[red]Back",
    ]
    choice = ColorMenu.select(options, title="Open browser?", esc=2)
    if choice == 3:
        exit(0)
    return None if choice == 2 else choice == 0


def ask_and_run_browser_flow(run: Callable[[bool], object]) -> None:
    """ask_open_browser() + run_browser_flow(); Back → nothing is run."""
    open_browser = ask_open_browser()
    if open_browser is not None:
        run_browser_flow(run, headless=not open_browser)


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
