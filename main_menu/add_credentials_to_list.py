import csv
import re

from rich import print

from classes.projects.Project import Project
from classes.utils.WPPaths import WPPaths
from main_menu import saved_project
from py_libs.Clipboard import Clipboard
from py_libs.InputValidator import InputValidator
from py_libs.Print import Print


def _read_clipboard() -> tuple[str, str, str] | None:
    lines = Clipboard.read().splitlines()
    if len(lines) != 3:
        Print.error(
            f"Clipboard must have exactly 3 lines (domain, login, password), found: {len(lines)}"
        )
        return None
    url, login, password = (line.strip() for line in lines)

    # keep only the origin (scheme + domain), no path or trailing slash
    match = re.match(r"^(https?://[^/?#\s]+)", url)
    if match:
        url = match.group(1)

    if not re.fullmatch(r"https?://\S+", url):
        Print.error(f"First line doesn't look like a url: '{url}'")
        return None
    if not login or re.search(r"\s", login):
        Print.error(f"Second line (login) is invalid: '{login}'")
        return None
    if not password or re.search(r"\s", password):
        Print.error(f"Third line (password) is invalid: '{password}'")
        return None
    for field in (url, login, password):
        if "," in field:
            Print.error(f"Field must not contain a comma: '{field}'")
            return None
    return url, login, password


def _print_clipboard_hint() -> None:
    print("[yellow]Clipboard must contain 3 lines:")
    print("[blue]  domain")
    print("[blue]  login")
    print("[blue]  password")


def add_credentials_to_list() -> bool:
    """Append a new site to list.csv; True if added (it's then the saved project)."""
    credentials = _read_clipboard()
    if credentials is None:
        _print_clipboard_hint()
        return False
    url, login, password = credentials
    print(f"[green]From clipboard: {url} | {login}")

    theme = input("Theme name: ").strip()
    if not theme:
        Print.error("Theme name can't be empty.")
        return False
    if "," in theme:
        Print.error("Theme name must not contain a comma.")
        return False
    new_row = [theme, login, password, url]
    new_line = ",".join(new_row)

    csv_path = WPPaths.get_list_csv_path()
    with open(csv_path) as f:
        rows = list(csv.reader(f))

    if any(row[:4] == new_row for row in rows):
        Print.error(f"Theme '{theme}' with this url/login/password is already in {csv_path}")
        return False

    existing = next((row for row in rows if row and row[0] == theme), None)
    if existing:
        print(f"Original: {','.join(existing)}")
        print(f"New:      {new_line}")
        if not InputValidator.get_bool("Data differs. Append a new row? [y/n]: "):
            print("Cancelled.")
            return False

    content = csv_path.read_bytes()
    needs_newline = bool(content) and not content.endswith(b"\n")
    with open(csv_path, "a") as f:
        f.write(("\n" if needs_newline else "") + new_line + "\n")

    saved_project.save(Project.from_row(new_row))
    print(f"[green]Added to {csv_path}: {new_line}")
    return True
