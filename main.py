#!/usr/bin/python3

import argparse

from py_libs.Menu import Menu
from classes.utils.WPPaths import WPPaths
from main_menu.acf_func import acf_func
from main_menu.backup_menu import backup_menu
from main_menu.contact_form_menu import contact_form_menu
from main_menu.file_menu import file_menu
from main_menu.image_menu import image_menu
from main_menu.init import init, reset_settings
from classes.pages.Page import Page
from classes.pages.RankMathMetabox import RankMathMetabox
from main_menu.page_menu import page_menu
from main_menu.page_theme_file_menu import page_theme_file_menu
from main_menu.post_menu import post_menu
from main_menu.plugins_menu import plugins_menu
from main_menu.site_settings_menu import site_settings_menu
from main_menu.taxonomy_menu import taxonomy_menu
from main_menu.theme_menu import theme_menu
from main_menu.use_from_list_menu import use_from_list_menu
from main_menu.wp_menu_locations import wp_menu_locations
from modules.check_is_wp import check_is_wp


def menu_items(to_import: bool = False):
    """
    (label, action, loop_back, color) — loop_back=False exits after action.
    """
    return [
        # wp content
        ("ACF", lambda: acf_func(to_import), True, "green"),
        ("Plugins", plugins_menu, True, "green"),
        ("Backups", backup_menu, True, "green"),
        ("Images", image_menu, True, "green"),
        ("Pages / Posts", page_menu, False, "green"),
        ("Taxonomy", taxonomy_menu, True, "green"),
        ("Themes", theme_menu, True, "green"),
        ("Menus", wp_menu_locations, True, "green"),
        # files / forms
        ("Contact Form", contact_form_menu, True, "blue"),
        ("Files", file_menu, True, "blue"),
        ("Root template", page_theme_file_menu, True, "blue"),
        ("Use from list", use_from_list_menu, True, "blue"),
        # settings
        ("Site Settings", site_settings_menu, True, "yellow"),
        ("Init", init, False, "yellow"),
        ("Reset Settings", reset_settings, False, "yellow"),
    ]


def select_menu_option() -> int:
    labels = [f"[{color}]{label}" for label, _, _, color in menu_items()]
    return Menu.select_fzf_menu(labels) or 0


def menu(
    to_import: bool = False,
    menu_acf: bool = False,
    menu_plugins: bool = False,
    menu_pages: bool = False,
    menu_posts: bool = False,
    page_ignore: bool = False,
    rank_math: bool = False,
    rank_math_page: bool = False,
    menu_backups: bool = False,
    menu_images: bool = False,
    menu_menus: bool = False,
    menu_files: bool = False,
    menu_taxonomy: bool = False,
    menu_page_theme_file: bool = False,
    menu_use_from_list: bool = False,
):
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
    elif menu_page_theme_file:
        page_theme_file_menu()
        return menu()
    elif menu_posts:
        post_menu()
        exit(0)
    elif rank_math_page:
        RankMathMetabox.toggle(post_type="page")
        exit(0)
    elif rank_math:
        RankMathMetabox.toggle()
        exit(0)
    elif page_ignore:
        Page.ignore_page()
        exit(0)
    elif menu_pages:
        page_menu()
        exit(0)
    elif menu_taxonomy:
        taxonomy_menu()
        return menu()
    elif menu_use_from_list:
        use_from_list_menu()
        return menu()

    choice = select_menu_option()
    if choice == 0:
        print("Exiting the program. Goodbye!")
        exit(0)

    _, action, loop_back, _ = menu_items(to_import)[choice - 1]
    action()
    if loop_back:
        menu()
    exit(0)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="""\
Shell aliases (defined in ~/dotfiles/zsh_modules/zsh_python):
  wb    -> main.py                       (interactive menu)
  wba   -> main.py --menu-acf
  wbp   -> main.py --menu-plugins
  wbg   -> main.py --menu-pages
  wbgo  -> main.py --menu-posts
  wbgi  -> main.py --page-ignore
  wbgr  -> main.py --rank-math
  wbgrp -> main.py --rank-math-page
  wbt   -> main.py --menu-taxonomy
  wbb   -> main.py --menu-backups
  wbi   -> main.py --menu-images
  wbm   -> main.py --menu-wp-menus
  wbf   -> main.py --menu-files
  wbfp  -> main.py --menu-page-theme-file
""",
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
        "--menu-pages", action="store_true", help="Directly open the Pages menu"
    )
    parser.add_argument(
        "--menu-posts", action="store_true", help="Directly open the Posts menu"
    )
    parser.add_argument(
        "--page-ignore",
        "--pi",
        action="store_true",
        help="Directly run 'Ignore page' from the Pages menu, then exit",
    )
    parser.add_argument(
        "--rank-math",
        "--rmm",
        action="store_true",
        help=(
            "Toggle Rank Math metaboxes (Screen Options) in the editor, "
            "then exit"
        ),
    )
    parser.add_argument(
        "--rank-math-page",
        "--rmp",
        action="store_true",
        help="Toggle Rank Math metaboxes for Pages (no post type prompt)",
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
    parser.add_argument(
        "--menu-taxonomy",
        action="store_true",
        help="Directly open the Taxonomy menu",
    )
    parser.add_argument(
        "--menu-page-theme-file",
        "--ptf",
        action="store_true",
        help="Directly open the Page Theme File menu",
    )
    parser.add_argument(
        "--use-from-list",
        action="store_true",
        help="Directly open the Use from list menu",
    )
    args = parser.parse_args()
    check_is_wp()
    WPPaths.initialize()
    menu(
        to_import=args.to_import,
        menu_acf=args.menu_acf,
        menu_plugins=args.menu_plugins,
        menu_pages=args.menu_pages,
        menu_posts=args.menu_posts,
        page_ignore=args.page_ignore,
        rank_math=args.rank_math,
        rank_math_page=args.rank_math_page,
        menu_backups=args.menu_backups,
        menu_images=args.menu_images,
        menu_menus=args.menu_wp_menus,
        menu_files=args.menu_files,
        menu_taxonomy=args.menu_taxonomy,
        menu_page_theme_file=args.menu_page_theme_file,
        menu_use_from_list=args.use_from_list,
    )
