from classes.theme.Theme import Theme
from classes.utils.ColorMenu import ColorMenu


def theme_menu():
    from py_libs.Command import Command

    options = [
        "[green]List all themes",
        "[blue]Install theme",
        "[yellow]Activate theme",
        "[yellow]Deactivate theme",
        "[red]Delete theme",
    ]

    while True:
        choice = ColorMenu.select(options)
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
        elif choice == 5:
            break
