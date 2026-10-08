from classes.theme.Theme import Theme
from main_menu.table_menu import BACK, table_menu


def theme_menu():
    from py_libs.Command import Command

    options = [
        "List all themes",
        "Install theme",
        "Activate theme",
        "Deactivate theme",
        "Delete theme",
    ]

    while True:
        choice = table_menu("Themes", options, red_options={"Delete theme"})
        if choice == 0:
            Command.run("wp theme list")
        elif choice == 1:
            Theme.install_theme()
        elif choice == 2:
            Theme.activate_theme()
        elif choice == 3:
            Theme.deactivate_theme()
        elif choice == 4:
            Theme.delete_theme()
        elif choice == BACK:
            break
