from classes.acf.AcfTransfer import AcfTransfer
from classes.acf.field.FieldMenu import FieldMenu


def field_menu(section_file_json_path):
    f_menu = FieldMenu(section_file_json_path)
    f_menu.show_all()
    # f_menu.create_field()
    f_menu.move_field()
    f_menu.show_all()
    to_upload = input("Do you want to upload the changes? (y/n): ").strip().lower()
    if to_upload == "y":
        AcfTransfer.wp_import()
        print("Changes uploaded successfully.")
    else:
        print("Changes not uploaded.")
    # while True:
    #     choice = input("Do you want to create another field? (y/n): ").strip().lower()
    #     if choice == "y":
    #         f_menu.create_field()
    #         f_menu.show_all()
    #     elif choice == "n":
    #         print("Exiting field menu.")
    #         break
    #     else:
    #         print("Invalid choice. Please enter 'y' or 'n'.")
