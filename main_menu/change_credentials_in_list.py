import csv
import re

from rich import print
from rich.markup import escape

from classes.projects.Project import Project
from classes.utils.WPPaths import WPPaths
from main_menu import saved_project
from py_libs.InputValidator import InputValidator
from py_libs.Menu import Menu
from classes.utils.ColorMenu import ColorMenu
from py_libs.Print import Print

# list.csv columns: title,login,password,url[,login_path]
FIELDS = ["Title", "Login", "Password", "Url", "Login path"]


def _validate(field_index: int, value: str) -> str | None:
    """Return the value to store, or None (error already printed)."""
    if "," in value:
        Print.error("Value must not contain a comma.")
        return None
    if field_index == 4:
        # login path is optional — empty removes it; no slashes around
        return value.strip("/")
    if not value or re.search(r"\s", value):
        Print.error(f"{FIELDS[field_index]} must not be empty or contain spaces.")
        return None
    if field_index == 3:
        # keep only the origin (scheme + domain), like add_credentials_to_list
        match = re.match(r"^(https?://[^/?#\s]+)", value)
        if not match:
            Print.error(f"Doesn't look like a url: '{value}'")
            return None
        return match.group(1)
    return value


def change_credentials_in_list():
    csv_path = WPPaths.get_list_csv_path()
    lines = csv_path.read_text().splitlines()
    # (line number in the file, parsed row) — edit exactly that line, keep the rest as is
    entries = [
        (i, next(csv.reader([line])))
        for i, line in enumerate(lines)
        if line.strip()
    ]
    # the project saved in "Use from list" — no search then
    saved_key = saved_project.load_key()
    picked = next(
        (
            i
            for i, (_, row) in enumerate(entries)
            if saved_key and len(row) >= 4 and saved_project.matches(Project.from_row(row), saved_key)
        ),
        -1,
    )
    if picked == -1:
        labels = [" | ".join(row) for _, row in entries]
        picked = Menu.select_fzf(labels)
        if picked == -1:
            return
    line_index, row = entries[picked]
    row = row + [""] * (len(FIELDS) - len(row))

    back, exit_index = len(FIELDS), len(FIELDS) + 1
    labels = [
        f"[{'blue' if i % 2 == 0 else 'green'}]{name}:[/] {escape(row[i])}"
        for i, name in enumerate(FIELDS)
    ] + ["[red]Back"]
    field_index = ColorMenu.select(labels, title=f"Change {row[0]}", esc=back)
    if field_index == back:
        return
    if field_index == exit_index:
        exit(0)

    value = _validate(field_index, input(f"New {FIELDS[field_index]}: ").strip())
    if value is None:
        return

    new_row = row.copy()
    new_row[field_index] = value
    # no login path → write the 4-column form
    new_line = ",".join(new_row if new_row[4] else new_row[:4])
    if new_line == lines[line_index]:
        Print.info("Nothing changed.")
        return

    print(f"Original: {lines[line_index]}")
    print(f"New:      {new_line}")
    if not InputValidator.get_bool("Save? [y/n]: "):
        print("Cancelled.")
        return

    lines[line_index] = new_line
    csv_path.write_text("\n".join(lines) + "\n")
    # title/url may have changed — keep the saved project pointing at this row
    saved_project.save(Project.from_row(new_line.split(",")))
    print(f"[green]Saved to {csv_path}")
