from rich import print

from classes.projects.Project import Project
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

    # imported here: importing WPPlaywright configures logging for the whole process
    from classes.selenium.WPPlaywrightReinstallAltuofianco import (
        WPPlaywrightReinstallAltuofianco,
    )

    WPPlaywrightReinstallAltuofianco(project["title"]).start()
    exit(0)


def use_from_list_menu():
    options = [
        "Reinstall Altuofianco",
        "Exit",
    ]
    row_styles = {
        0: "bold blue",
        1: "bold red",
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
