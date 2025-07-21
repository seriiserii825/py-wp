from classes.acf.AcfTransfer import AcfTransfer
from classes.acf.field.FieldMenu import FieldMenu
from classes.utils.Menu import Menu


def field_menu(section_file_json_path):
    while True:
        acf_menu(section_file_json_path)


def acf_menu(section_file_json_path):
    f_menu = FieldMenu(section_file_json_path)
    f_menu.show_all()
    menu_headers = ["Index", "Option"]
    menu_rows = [
        ["0", "Create new field"],
        ["1", "Move field"],
        ["2", "Edit field"],
        ["3", "Delete field"],
        ["4", "Delete multiple fields"],
        ["5", "Copy group to clipboard"],
        ["6", "Upload changes to WordPress"],
        ["7", "Exit"],
    ]
    Menu.display("Welcome to ACF Field Menu", menu_headers, menu_rows)
    choice = Menu.choose_option()
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
