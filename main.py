#!/usr/bin/python3

from classes.utils.Menu import Menu
from classes.utils.WPPaths import WPPaths
from main_menu.acf_func import acf_func
from main_menu.backup_menu import backup_menu
from main_menu.contact_form_menu import contact_form_menu
from main_menu.image_menu import image_menu
from main_menu.init import init, reset_settings
from main_menu.page_menu import page_menu
from main_menu.plugins_menu import plugins_menu
from main_menu.theme_menu import theme_menu
from modules.check_is_wp import check_is_wp


def menu():
    headers = ["Index", "Option"]

    row_styles = {
        0: "bold blue",
        1: "bold green",
        2: "bold blue",
        3: "bold green",
        4: "bold yellow",
        5: "bold green",
        6: "bold blue",
        7: "bold green",
        8: "bold blue",
        9: "bold red"
    }
    rows = [
        ["0", "ACF"],
        ["1", "Plugins"],
        ["2", "Backups"],
        ["3", "Init"],
        ["4", "Reset Settings"],
        ["5", "Images"],
        ["6", "Pages"],
        ["7", "Themes"],
        ["8", "Contact Form"],
        ["9", "Exit"]
    ]
    Menu.display("Main Menu", headers, rows, row_styles=row_styles)
    choice = Menu.choose_option()
    if choice == 0:
        acf_func()
        menu()
    elif choice == 1:
        plugins_menu()
        menu()
    elif choice == 2:
        backup_menu()  # noqa: F821
        menu()
    elif choice == 3:
        init()
        exit(0)
    elif choice == 4:
        reset_settings()
        exit(0)
    elif choice == 5:
        image_menu()
        menu()
    elif choice == 6:
        page_menu()
        menu()
    elif choice == 7:
        theme_menu()
        menu()
    elif choice == 8:
        contact_form_menu()
        menu()
    elif choice == 9:
        print("Exiting the program. Goodbye!")
        exit(0)
    else:
        print("Invalid choice. Please try again.")
        menu()


if __name__ == "__main__":
    check_is_wp()
    WPPaths.initialize()
    menu()
