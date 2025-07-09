#!/usr/bin/python3

from main_menu.acf_func import acf_func
from main_menu.init import init
from modules.check_is_wp import check_is_wp


def menu():
    init()
    acf_func()


if __name__ == "__main__":
    check_is_wp()
    menu()
