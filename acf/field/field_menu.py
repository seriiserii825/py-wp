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

    while True:
        f_menu.show_all()
        menu_options = [
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
            f_menu.create_field()
        elif choice == 1:
            f_menu.move_field()
        elif choice == 2:
            f_menu.edit_field()
        elif choice == 3:
            f_menu.delete_field()
        elif choice == 4:
            f_menu.delete_fields()
        elif choice == 5:
            f_menu.copy_group_to_clipboard()
        elif choice == 6:
            upload_changes()
        elif choice == 7:
            print("Exiting ACF Field Menu.")
            break
        else:
            print("Invalid choice. Please try again.")


def upload_changes():
    print("Uploading changes to WordPress...")
    copy_acf_folder_to_downloads()
    AcfTransfer.wp_import()


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
