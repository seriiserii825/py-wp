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


def menu(
    to_import: bool = False,
    menu_acf: bool = False,
    menu_plugins: bool = False,
    menu_backups: bool = False,
    menu_images: bool = False,
    menu_menus: bool = False,
    menu_files: bool = False,
):
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
    if menu_acf:
        acf_func(to_import)
        return menu()
    elif menu_plugins:
        plugins_menu()
        return menu()
    elif menu_backups:
        backup_menu()
        return menu()
    elif menu_images:
        image_menu()
        return menu()
    elif menu_menus:
        wp_menu_locations()
        return menu()
    elif menu_files:
        file_menu()
        return menu()

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
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""\
ACF import/export notes:
  Plain `python main.py` (no --to-import) exports: it overwrites acf/*.json
  with whatever is currently live in the WordPress DB, including its field
  ORDER. If fields were ever reordered directly in wp-admin (drag & drop)
  without going through this tool, that live order can be wrong/scrambled,
  and a plain export will copy that broken order into acf/*.json, clobbering
  any good order you had locally.

  acf-snapshots/*.json (next to acf/) is NOT touched by export. It is the
  separate, trusted record of the correct field order, taken the last time
  someone confirmed it was right.

  To fix a scrambled field order in WordPress (the symptom: fields/tabs show
  in the wrong order, or split apart, in wp-admin "Edit field group"):

    python main.py --menu-acf --to-import

  `--menu-acf` is required together with `--to-import` to skip the
  interactive fzf menu and run the import immediately. Running --to-import
  by itself still asks you to pick "ACF" from the menu first.

  What --to-import actually does (AcfTransfer.wp_import):
    1. Re-applies the order recorded in acf-snapshots/*.json onto each
       acf/*.json group (does NOT change the snapshot itself).
    2. Runs `wp acf clean` + `wp acf import --all` to push field
       definitions into the WordPress DB.
    3. Writes the snapshot order directly into wp_posts.menu_order for
       every field, because `wp acf import` does not reorder fields that
       already exist in the DB on its own.

  If acf-snapshots/*.json itself is missing or wrong for a group, fix the
  order once in wp-admin (or in acf/*.json) and run the interactive ACF
  Field Menu's "Reorder from snapshot" / upload flow to regenerate it,
  before relying on --to-import again.
""",
    )
    parser.add_argument(
        "--to-import",
        action="store_true",
        help=(
            "Import ACF data instead of exporting: pushes acf/*.json into "
            "WordPress and re-applies the field order from "
            "acf-snapshots/*.json (use together with --menu-acf to skip the "
            "menu prompt; see notes below)"
        ),
    )
    parser.add_argument(
        "--menu-acf", action="store_true", help="Directly open the ACF menu"
    )
    parser.add_argument(
        "--menu-plugins", action="store_true", help="Directly open the Plugins menu"
    )
    parser.add_argument(
        "--menu-backups", action="store_true", help="Directly open the Backups menu"
    )
    parser.add_argument(
        "--menu-images", action="store_true", help="Directly open the Images menu"
    )
    parser.add_argument(
        "--menu-wp-menus", action="store_true", help="Directly open the Menus menu"
    )
    parser.add_argument(
        "--menu-files", action="store_true", help="Directly open the Files menu"
    )
    args = parser.parse_args()
    check_is_wp()
    WPPaths.initialize()
    menu(
        to_import=args.to_import,
        menu_acf=args.menu_acf,
        menu_plugins=args.menu_plugins,
        menu_backups=args.menu_backups,
        menu_images=args.menu_images,
        menu_menus=args.menu_wp_menus,
        menu_files=args.menu_files,
    )
