from classes.acf.AcfTransfer import AcfTransfer
from classes.acf.field.FieldMenu import FieldMenu
from classes.utils.Menu import Menu


def field_menu(section_file_json_path):
    while True:
        acf_menu(section_file_json_path)


def acf_menu(section_file_json_path):
    f_menu = FieldMenu(section_file_json_path)
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
        f_menu.show_all()
    elif choice == 1:
        f_menu.move_field()
        f_menu.show_all()
    elif choice == 2:
        f_menu.edit_field()
        f_menu.show_all()
    elif choice == 3:
        f_menu.delete_field()
        f_menu.show_all()
    elif choice == 4:
        f_menu.delete_fields()
        f_menu.show_all()
    elif choice == 5:
        f_menu.show_all()
        f_menu.copy_group_to_clipboard()
    elif choice == 6:
        upload_changes()
        f_menu.show_all()
    elif choice == 7:
        print("Exiting ACF Field Menu.")
        exit()
    else:
        print("Invalid choice. Please try again.")
        acf_menu(section_file_json_path)


def upload_changes():
    print("Uploading changes to WordPress...")
    AcfTransfer.wp_import()
