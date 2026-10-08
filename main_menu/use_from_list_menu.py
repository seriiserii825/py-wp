import time

from rich import print

from classes.projects.Project import Project
from main_menu.add_credentials_to_list import add_credentials_to_list
from main_menu.ask_open_browser import ask_open_browser, run_browser_flow
from main_menu import saved_project
from main_menu.change_credentials_in_list import change_credentials_in_list
from py_libs.Clipboard import Clipboard
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


def _search_and_save() -> dict[str, str] | None:
    """Search a project anew: the saved one is dropped, the found one saved."""
    saved_project.clear()
    project = _select_project()
    if project is not None:
        saved_project.save(project)
    return project


def _saved_or_search() -> dict[str, str] | None:
    return saved_project.load() or _search_and_save()


def reinstall_altuofianco():
    project = _search_and_save()
    if project is None:
        return
    print(f"[green]Site: [bold]{_project_label(project)}")
    open_browser = ask_open_browser()

    # imported here: importing WPPlaywright configures logging for the whole process
    from classes.selenium.WPPlaywrightReinstallAltuofianco import (
        WPPlaywrightReinstallAltuofianco,
    )

    run_browser_flow(
        lambda headless: WPPlaywrightReinstallAltuofianco(
            project["title"], headless=headless
        ).start(),
        headless=not open_browser,
    )


def _project_full_line(project: dict[str, str]) -> str:
    fields = [project["title"], project["url"], project["login"], project["password"]]
    if project.get("gestione"):
        fields.append(project["gestione"])
    return " | ".join(fields)


def find_project():
    saved_project.clear()
    projects = Project.get_all_projects()
    lines = [_project_full_line(p) for p in projects]
    index = Menu.select_fzf(lines)
    if index == -1:
        return
    saved_project.save(projects[index])
    print(f"[green]{lines[index]}")


# pause between the two copies so the clipboard manager stores both entries
COPY_DELAY_SECONDS = 1.0


def copy_credentials():
    """Password first, login after a delay: the login ends up in the clipboard,
    the password stays one entry back in the clipboard history."""
    project = _saved_or_search()
    if project is None:
        return
    print(f"[green]Site: [bold]{_project_label(project)}")
    Clipboard.write(project["password"], show=False)
    time.sleep(COPY_DELAY_SECONDS)
    Clipboard.write(project["login"])
    print(f"[green]Copied: password, then login ({project['login']})")


def use_from_list_menu():
    saved_project.print_header()
    options = [
        "Reinstall Altuofianco",
        "Find project",
        "Add credentials to list",
        "Change credentials",
        "Copy credentials",
        "Exit",
    ]
    row_styles = {
        0: "bold blue",
        1: "bold green",
        2: "bold blue",
        3: "bold green",
        4: "bold blue",
        5: "bold red",
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
    elif choice == 3:
        change_credentials_in_list()
        use_from_list_menu()
    elif choice == 4:
        copy_credentials()
        use_from_list_menu()
