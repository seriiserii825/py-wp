import time

from rich import print

from classes.projects.Project import Project
from main_menu.add_credentials_to_list import add_credentials_to_list
from main_menu.ask_open_browser import ask_open_browser, run_browser_flow
from main_menu import saved_project
from main_menu.change_credentials_in_list import change_credentials_in_list
from main_menu.table_menu import BACK, table_menu
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
    choice = table_menu("Find site", options)
    if choice == BACK:
        return None

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


def reinstall_altuofianco():
    project = _search_and_save()
    if project is None:
        return
    print(f"[green]Site: [bold]{_project_label(project)}")
    open_browser = ask_open_browser()
    if open_browser is None:
        # Back: the project stays picked, its submenu is still useful
        project_menu()
        return

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
    project_menu()


def _run_backup_flow(playwright_cls):
    """Pick a site, ask browser / headless, run a WPPlaywright*Backup subclass
    on it, then open the Project submenu."""
    project = _search_and_save()
    if project is None:
        return
    theme_name = project["title"]

    print(f"[green]Site: [bold]{_project_label(project)}")
    open_browser = ask_open_browser()
    if open_browser is None:
        # Back: the project stays picked, its submenu is still useful
        project_menu()
        return

    run_browser_flow(
        lambda headless: playwright_cls(theme_name, headless=headless).start(),
        headless=not open_browser,
    )
    project_menu()


def create_backup_on_server():
    # imported here: importing WPPlaywright configures logging for the whole process
    from classes.selenium.WPPlaywrightCreateBackup import WPPlaywrightCreateBackup

    _run_backup_flow(WPPlaywrightCreateBackup)


def download_last_backup_from_server():
    # imported here: importing WPPlaywright configures logging for the whole process
    from classes.selenium.WPPlaywrightDownloadBackup import WPPlaywrightDownloadBackup

    _run_backup_flow(WPPlaywrightDownloadBackup)


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
    project_menu()


# pause between the two copies so the clipboard manager stores both entries
COPY_DELAY_SECONDS = 1.0


def copy_credentials():
    """Password first, login after a delay: the login ends up in the clipboard,
    the password stays one entry back in the clipboard history."""
    project = saved_project.load()
    if project is None:
        Print.error("No saved project (Reinstall / Find project first).")
        return
    print(f"[green]Site: [bold]{_project_label(project)}")
    Clipboard.write(project["password"], show=False)
    time.sleep(COPY_DELAY_SECONDS)
    Clipboard.write(project["login"])
    print(f"[green]Copied: password, then login ({project['login']})")


def project_menu():
    """Actions on the project saved by Reinstall / Find project
    (saved-project.txt); shown right after one was picked."""
    if saved_project.load() is None:
        return
    saved_project.print_header()
    options = [
        "Copy credentials",
        "Change credentials",
    ]
    choice = table_menu("Project", options)
    if choice == 0:
        copy_credentials()
        project_menu()
    elif choice == 1:
        change_credentials_in_list()
        project_menu()
    # Back → return to Use from list


def use_from_list_menu():
    options = [
        "Reinstall Altuofianco",
        "Create Backup on Server",
        "Download Last Backup from Server",
        "Find project",
        "Add credentials",
    ]
    choice = table_menu("Use from list", options)
    if choice == 0:
        reinstall_altuofianco()
        use_from_list_menu()
    elif choice == 1:
        create_backup_on_server()
        use_from_list_menu()
    elif choice == 2:
        download_last_backup_from_server()
        use_from_list_menu()
    elif choice == 3:
        find_project()
        use_from_list_menu()
    elif choice == 4:
        # a new site isn't in list.csv yet — once added it's the saved project
        if add_credentials_to_list():
            project_menu()
        use_from_list_menu()
    # Back → return to the main menu (main.py shows it after we return)
