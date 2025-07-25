#!/usr/bin/python3

from classes.utils.Menu import Menu
from classes.utils.WPPaths import WPPaths
from main_menu.acf_func import acf_func
from main_menu.plugins_menu import plugins_menu
from modules.check_is_wp import check_is_wp


def menu():
    acf_func()
    # headers = ["Index", "Option"]
    #
    # row_styles = {
    #     0: "bold blue",
    #     1: "bold green",
    #     2: "bold red"
    # }
    # rows = [
    #     ["0", "ACF"],
    #     ["1", "Plugins"],
    #     ["2", "Exit"]
    # ]
    # Menu.display("Main Menu", headers, rows, row_styles=row_styles)
    # choice = Menu.choose_option()
    # if choice == 0:
    #     acf_func()
    #     menu()
    # elif choice == 1:
    #     plugins_menu()
    #     menu()
    # elif choice == 2:
    #     print("Exiting the program. Goodbye!")
    #     exit(0)
    # else:
    #     print("Invalid choice. Please try again.")
    #     menu()
    # backup_menu()
    # plugins_menu()


if __name__ == "__main__":
    WPPaths.initialize()
    check_is_wp()
    menu()
