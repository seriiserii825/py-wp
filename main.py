#!/usr/bin/python3

from classes.utils.WPPaths import WPPaths
from main_menu.acf_func import acf_func
from main_menu.backup_menu import backup_menu
from main_menu.plugins_menu import plugins_menu
from modules.check_is_wp import check_is_wp


def menu():
    # acf_func()
    # backup_menu()
    plugins_menu()


if __name__ == "__main__":
    WPPaths.initialize()
    check_is_wp()
    menu()
