import shutil
import subprocess

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
    current_view = VIEW_ALL  # first open: show all

    def render(index: int = 0):
        if current_view == VIEW_ALL:
            print("=== ACF Field Menu: Showing All Fields ===")
            f_menu.show_all()
        else:
            print("=== ACF Field Menu: Showing Only Tab/Group Fields ===")
            f_menu.show_only_tab_group(index)

    # initial render
    render()

    while True:
        menu_options = [
            "Show All Fields",
            "Show Only Tab/Group Fields",
            "Create new field",
            "Move field",
            "Edit field",
            "Delete field",
            "Delete multiple fields",
            "Copy group to clipboard",
            "Upload changes to WordPress",
            "Exit",
        ]
        choice = Menu.select_with_fzf(menu_options)
        if choice == 0:
            current_view = VIEW_ALL
            f_menu.show_all()
            render()
        elif choice == 1:
            current_view = VIEW_TABS
            f_menu.show_only_tab_group()
            render()
        elif choice == 2:
            f_menu.create_field()
            render()
        elif choice == 3:
            try:
                index = f_menu.move_field()
                render(int(index))
            except Exception as e:
                print(f"Error moving field: {e}")
                render()
        elif choice == 4:
            f_menu.edit_field()
            render()
        elif choice == 5:
            f_menu.delete_field()
            render()
        elif choice == 6:
            f_menu.delete_fields()
            render()
        elif choice == 7:
            f_menu.copy_group_to_clipboard()
            render()
        elif choice == 8:
            upload_changes(section_file_json_path=section_file_json_path)
        elif choice == 9:
            print("Exiting ACF Field Menu.")
            break
        else:
            print("Invalid choice. Please try again.")


def upload_changes(section_file_json_path: str | Path):
    print("Uploading changes to WordPress...")
    copy_acf_folder_to_downloads()
    AcfTransfer.wp_import()
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
    """
    section_file_json_path — путь до JSON файла (str или Path).
    Вызывает bash-скрипт fix-order.sh и передает ему этот путь.
    """
    script_dir = WPPaths.get_script_dir_path()
    script = f"{script_dir}/bash-scripts/json-acf-menu-order.sh"

    section_file_json_path = Path(section_file_json_path).resolve()

    try:
        result = subprocess.run(
            [script, str(section_file_json_path)],
            check=True,
            capture_output=True,
            text=True
        )
        print("stdout:", result.stdout)
        print("stderr:", result.stderr)
        return result.returncode
    except subprocess.CalledProcessError as e:
        print(f"Error running {script}: {e}")
        print("stdout:", e.stdout)
        print("stderr:", e.stderr)
        return e.returncode
