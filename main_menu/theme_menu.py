from classes.theme.Theme import Theme


def theme_menu():
    from classes.utils.Select import Select
    from classes.utils.Command import Command

    options = [
        "List all themes",
        "Install theme",
        "Activate theme",
        "Deactivate theme",
        "Delete theme",
        "Exit",
    ]

    while True:
        choice = Select.select_one(options)
        if choice == "List all themes":
            Command.run("wp theme list")
        elif choice == "Install theme":
            Theme.install_theme()
        elif choice == "Activate theme":
            Theme.activate_theme()
        elif choice == "Deactivate theme":
            Theme.deactivate_theme()
        elif choice == "Delete theme":
            Theme.delete_theme()
        elif choice == "Exit":
            break
