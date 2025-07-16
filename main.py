#!/usr/bin/python3

from classes.utils.PathHelper import PathHelper
from main_menu.acf_func import acf_func
from main_menu.init import init
from modules.check_is_wp import check_is_wp
from path_urils import CWD, ENTRY_POINT, MODULE_DIR


def menu():
    ph = PathHelper()
    print(f"Entry Point: {ph.get_entry_point}")
    print(f"Module Directory: {ph.get_entry_dir}")
    print(f"Current Working Directory: {ph.get_cwd}")


if __name__ == "__main__":
    check_is_wp()
    menu()
