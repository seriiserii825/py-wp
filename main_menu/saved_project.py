"""The project picked last in "Use from list", kept in saved-project.txt (next
to list.csv) so the other items don't ask for it again.

Only title + url are stored (two lines); login/password are always read fresh
from list.csv. The file is gitignored.
"""
from urllib.parse import urlparse

from rich import print

from classes.projects.Project import Project
from classes.utils.WPPaths import WPPaths


def _path():
    return WPPaths.get_list_csv_path().parent / "saved-project.txt"


def save(project: dict[str, str]) -> None:
    _path().write_text(f"{project['title']}\n{project['url']}\n")


def clear() -> None:
    _path().unlink(missing_ok=True)


def matches(project: dict[str, str], saved: tuple[str, str]) -> bool:
    return (project["title"], project["url"]) == saved


def load_key() -> tuple[str, str] | None:
    """(title, url) from the file, None if nothing is saved."""
    path = _path()
    if not path.exists():
        return None
    lines = path.read_text().splitlines()
    if len(lines) < 2:
        return None
    return lines[0], lines[1]


def load() -> dict[str, str] | None:
    """The saved project as in list.csv; None if nothing saved or it's no longer there."""
    key = load_key()
    if key is None:
        return None
    return next((p for p in Project.get_all_projects() if matches(p, key)), None)


def print_header() -> None:
    """Always-visible line above the Use from list menu: what we work with."""
    project = load()
    if project is None:
        print("[yellow]No project selected (Reinstall / Find project select one)")
        return
    login_path = project.get("gestione")
    login = f"{project['url']}/{login_path}" if login_path else project["url"]
    print(
        f"[bold green]Project:[/bold green] {urlparse(project['url']).netloc}  "
        f"[bold green]Theme:[/bold green] {project['title']}  "
        f"[bold green]Site:[/bold green] {login}"
    )
