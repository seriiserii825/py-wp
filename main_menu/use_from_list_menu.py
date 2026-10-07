from rich import print

from classes.projects.Project import Project
from main_menu.add_credentials_to_list import add_credentials_to_list
from main_menu.ask_open_browser import ask_open_browser
from py_libs.Menu import Menu
from py_libs.Print import Print


def _project_label(project: dict[str, str]) -> str:
    return f"{project['title']} | {project['url']}"


def _select_project() -> dict[str, str] | None:
    options = [
        "Enter domain",
        "Search with fzf",
    ]
    row_styles = {
        0: "bold blue",
        1: "bold green",
    }
    Menu.display(
        "Find site",
        ["Index", "Option"],
        [[str(i), o] for i, o in enumerate(options)],
        row_styles=row_styles,
    )
    choice = Menu.choose_option()

    projects = Project.get_all_projects()
    if choice == 0:
        domain = input("Domain: ").strip().lower()
        if not domain:
            Print.error("Domain is empty.")
            return None
        projects = [p for p in projects if domain in p["url"].lower()]
        if not projects:
            Print.error(f"No site with domain '{domain}' in list.csv.")
            return None
        if len(projects) == 1:
            return projects[0]

    labels = [_project_label(p) for p in projects]
    index = Menu.select_fzf(labels)
    if index == -1:
        return None
    return projects[index]


def reinstall_altuofianco():
    project = _select_project()
    if project is None:
        return
    print(f"[green]Site: [bold]{_project_label(project)}")
    open_browser = ask_open_browser()

    # imported here: importing WPPlaywright configures logging for the whole process
    from classes.selenium.WPPlaywrightReinstallAltuofianco import (
        WPPlaywrightReinstallAltuofianco,
    )

    WPPlaywrightReinstallAltuofianco(
        project["title"], headless=not open_browser
    ).start()
    exit(0)


def _project_full_line(project: dict[str, str]) -> str:
    fields = [project["title"], project["url"], project["login"], project["password"]]
    if project.get("gestione"):
        fields.append(project["gestione"])
    return " | ".join(fields)


def find_project():
    projects = Project.get_all_projects()
    lines = [_project_full_line(p) for p in projects]
    index = Menu.select_fzf(lines)
    if index == -1:
        return
    print(f"[green]{lines[index]}")


def use_from_list_menu():
    options = [
        "Reinstall Altuofianco",
        "Find project",
        "Add credentials to list",
        "Exit",
    ]
    row_styles = {
        0: "bold blue",
        1: "bold green",
        2: "bold blue",
        3: "bold red",
    }
    Menu.display(
        "Use from list",
        ["Index", "Option"],
        [[str(i), o] for i, o in enumerate(options)],
        row_styles=row_styles,
    )
    choice = Menu.choose_option()
    if choice == 0:
        reinstall_altuofianco()
        use_from_list_menu()
    elif choice == 1:
        find_project()
        use_from_list_menu()
    elif choice == 2:
        add_credentials_to_list()
        use_from_list_menu()
