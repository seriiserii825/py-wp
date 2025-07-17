#!/usr/bin/python3

from classes.utils.PathHelper import PathHelper
from main_menu.acf_func import acf_func
from modules.check_is_wp import check_is_wp


def menu():
    acf_func()


if __name__ == "__main__":
    check_is_wp()
    menu()
