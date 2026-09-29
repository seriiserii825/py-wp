import sys

from rich.console import Console

console = Console()


class ExitApp:
    @staticmethod
    def confirm_and_exit() -> None:
        """Ask to exit the whole script, defaulting to no: Enter or 'n' cancels, 'y' exits."""
        value = console.input("Exit the script? (y/N, N - press Enter): ").strip().lower()
        if value in ("y", "yes"):
            console.print("[red]Goodbye!")
            sys.exit(0)
