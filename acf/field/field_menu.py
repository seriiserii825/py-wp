import shutil

from pathlib import Path
from rich import print
from classes.acf.AcfTransfer import AcfTransfer
from classes.acf.field.FieldMenu import FieldMenu
from main_menu.table_menu import BACK, table_menu
from classes.utils.WPPaths import WPPaths


def field_menu(section_file_json_path):
    acf_menu(section_file_json_path)


def acf_menu(section_file_json_path):
    f_menu = FieldMenu(section_file_json_path)

    VIEW_ALL = "all"
    VIEW_TABS = "tabs"
    VIEW_COLLAPSED = "collapsed"
    current_view = VIEW_ALL  # first open: show all
    selected_tab_index = 0

    def render():
        if current_view == VIEW_ALL:
            print("=== ACF Field Menu: Showing All Fields ===")
            f_menu.show_all()
        elif current_view == VIEW_COLLAPSED:
            print("=== ACF Field Menu: Collapsed ===")
            f_menu.show_collapsed()
        else:
            print("=== ACF Field Menu: Showing Only Tab/Group Fields ===")
            f_menu.show_only_tab_group(selected_tab_index)

    # initial render
    render()

    while True:
        menu_options = [
            "Show All Fields",
            "Show Only Tab/Group Fields",
            "Collapse All",
            "Order Fields",
            "Create new field",
            "Create predefined fields (from CSV)",
            "Move field",
            "Move multiple fields",
            "Edit field",
            "Delete field",
            "Delete multiple fields",
            "Duplicate field",
            "Toggle required by indexes",
            "Copy group to clipboard",
            "Upload changes to WordPress",
            "Reorder from snapshot",
        ]
        choice = table_menu(
            "ACF Field Menu",
            menu_options,
            red_options={"Delete field", "Delete multiple fields"},
        )
        if choice == 0:
            current_view = VIEW_ALL
            render()
        elif choice == 1:
            picked = f_menu.select_tab_group_index()
            if picked is not None:
                selected_tab_index = picked
                current_view = VIEW_TABS
            render()
        elif choice == 2:
            current_view = VIEW_COLLAPSED
            render()
        elif choice == 3:
            f_menu.reorder_fields()
            render()
        elif choice == 4:
            f_menu.create_field()
            render()
        elif choice == 5:
            f_menu.create_predefined_fields()
            render()
        elif choice == 6:
            print(
                "[yellow]Note: if the field is moved into another group/tab, "
                "that group must be opened ('Show Only Tab/Group Fields' or "
                "'Show All Fields') to see the result.[/yellow]"
            )
            try:
                f_menu.move_field()
                render()
            except Exception as e:
                print(f"Error moving field: {e}")
                render()
        elif choice == 7:
            print(
                "[yellow]Note: if the fields are moved into another group/tab, "
                "that group must be opened ('Show Only Tab/Group Fields' or "
                "'Show All Fields') to see the result.[/yellow]"
            )
            f_menu.move_multiple_fields()
            render()
        elif choice == 8:
            f_menu.edit_field()
            render()
        elif choice == 9:
            f_menu.delete_field()
            render()
        elif choice == 10:
            f_menu.delete_fields()
            render()
        elif choice == 11:
            f_menu.duplicate_field()
            render()
        elif choice == 12:
            f_menu.toggle_required()
            render()
        elif choice == 13:
            f_menu.copy_group_to_clipboard()
            render()
        elif choice == 14:
            upload_changes(section_file_json_path=section_file_json_path)
        elif choice == 15:
            try:
                f_menu.reorder_from_snapshot(WPPaths.get_theme_path())
                render()
            except FileNotFoundError as e:
                print(f"Snapshot not found: {e}")
            except Exception as e:
                print(f"Error reordering from snapshot: {e}")
        elif choice == BACK:
            print("Going back.")
            break


def upload_changes(section_file_json_path: str | Path):
    print("Uploading changes to WordPress...")
    copy_acf_folder_to_downloads()
    AcfTransfer.wp_import_single(section_file_json_path)
    print("Upload completed.")


def copy_acf_folder_to_downloads():
    theme_path = WPPaths.get_theme_path()
    acf_folder = theme_path / "acf"
    downloads_path = Path.home() / "Downloads"
    # copy to downloads
    if acf_folder.exists() and acf_folder.is_dir():
        destination = downloads_path / "acf"
        if destination.exists():
            shutil.rmtree(destination)
        shutil.copytree(acf_folder, destination)
        print(f"ACF folder copied to {destination}")
    else:
        print("ACF folder does not exist in the theme directory.")
