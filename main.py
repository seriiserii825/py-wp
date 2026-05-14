#!/usr/bin/python3

import argparse

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
from main_menu.site_settings_menu import site_settings_menu
from main_menu.theme_menu import theme_menu
from main_menu.wp_menu_locations import wp_menu_locations
from modules.check_is_wp import check_is_wp


def menu(to_import: bool = False):
    options = [
        "0).ACF",
        "01).Plugins",
        "02).Backups",
        "03).Images",
        "04).Pages",
        "05).Themes",
        "06).Menus",
        "07).Contact Form",
        "08).Files",
        "09).Site Settings",
        "10).Init",
        "11).Reset Settings",
        "12).Exit",
    ]
    choice = Menu.select_fzf(options)
    if choice == 0:
        acf_func(to_import)
        menu()
    elif choice == 1:
        plugins_menu()
        menu()
    elif choice == 2:
        backup_menu()  # noqa: F821
        menu()
    elif choice == 3:
        image_menu()
        menu()
    elif choice == 4:
        page_menu()
        exit(0)
    elif choice == 5:
        theme_menu()
        menu()
    elif choice == 6:
        wp_menu_locations()
        menu()
    elif choice == 7:
        contact_form_menu()
        menu()
    elif choice == 8:
        file_menu()
        menu()
    elif choice == 9:
        site_settings_menu()
        menu()
    elif choice == 10:
        init()
        exit(0)
    elif choice == 11:
        reset_settings()
        exit(0)
    elif choice == 12:
        print("Exiting the program. Goodbye!")
        exit(0)
    else:
        print("Invalid choice. Please try again.")
        exit(0)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--to-import", action="store_true", help="Import ACF data instead of exporting"
    )
    args = parser.parse_args()
    check_is_wp()
    WPPaths.initialize()
    menu(to_import=args.to_import)
