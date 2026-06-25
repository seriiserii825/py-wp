import shutil

from pathlib import Path
from classes.acf.AcfTransfer import AcfTransfer
from classes.acf.field.FieldMenu import FieldMenu
from classes.utils.Menu import Menu
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
            "0.Show All Fields",
            "1.Show Only Tab/Group Fields",
            "2.Collapse All",
            "3.Order Fields",
            "4.Create new field",
            "5.Move field",
            "6.Move multiple fields",
            "7.Edit field",
            "8.Delete field",
            "9.Delete multiple fields",
            "10.Duplicate field",
            "11.Toggle required by indexes",
            "12.Copy group to clipboard",
            "13.Upload changes to WordPress",
            "14.Reorder from snapshot",
            "15.Exit",
        ]
        choice = Menu.select_fzf(menu_options)
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
            try:
                f_menu.move_field()
                render()
            except Exception as e:
                print(f"Error moving field: {e}")
                render()
        elif choice == 6:
            f_menu.move_multiple_fields()
            render()
        elif choice == 7:
            f_menu.edit_field()
            render()
        elif choice == 8:
            f_menu.delete_field()
            render()
        elif choice == 9:
            f_menu.delete_fields()
            render()
        elif choice == 10:
            f_menu.duplicate_field()
            render()
        elif choice == 11:
            f_menu.toggle_required()
            render()
        elif choice == 12:
            f_menu.copy_group_to_clipboard()
            render()
        elif choice == 13:
            upload_changes(section_file_json_path=section_file_json_path)
        elif choice == 14:
            try:
                f_menu.reorder_from_snapshot(WPPaths.get_theme_path())
                render()
            except FileNotFoundError as e:
                print(f"Snapshot not found: {e}")
            except Exception as e:
                print(f"Error reordering from snapshot: {e}")
        elif choice == 15:
            print("Exiting ACF Field Menu.")
            break
        else:
            print("Invalid choice. Please try again.")


def upload_changes(section_file_json_path: str | Path):
    print("Uploading changes to WordPress...")
    copy_acf_folder_to_downloads()
    AcfTransfer.wp_import(current_section_path=section_file_json_path)
    print("Update field order from json file")
    update_fields_order(section_file_json_path=section_file_json_path)
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


def update_fields_order(section_file_json_path: str | Path):
    return AcfTransfer.push_menu_order_to_db(Path(section_file_json_path))
