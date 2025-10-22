#!/usr/bin/python3

from classes.utils.Menu import Menu
from classes.utils.WPPaths import WPPaths
from main_menu.acf_func import acf_func
from main_menu.backup_menu import backup_menu
from main_menu.contact_form_menu import contact_form_menu
from main_menu.file_menu import file_menu
from main_menu.image_menu import image_menu
from main_menu.init import init, reset_settings
from main_menu.page_menu import page_menu
from main_menu.plugins_menu import plugins_menu
from main_menu.theme_menu import theme_menu
from modules.check_is_wp import check_is_wp


def menu():
    options = [
        "0).ACF",
        "01).Plugins",
        "02).Backups",
        "03).Init",
        "04).Reset Settings",
        "05).Images",
        "06).Pages",
        "07).Themes",
        "08).Contact Form",
        "09).Files",
        "10).Exit"
    ]
    choice = Menu.select_fzf(options)
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
        file_menu()
        menu()
    elif choice == 10:
        print("Exiting the program. Goodbye!")
        exit(0)
    else:
        print("Invalid choice. Please try again.")
        exit(0)


if __name__ == "__main__":
    check_is_wp()
    WPPaths.initialize()
    menu()
