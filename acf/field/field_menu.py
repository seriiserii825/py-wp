from classes.acf.field.FieldMenu import FieldMenu


def field_menu(section_file_json_path):
    f_menu = FieldMenu(section_file_json_path)
    f_menu.show_all()
    f_menu.create_field()
    f_menu.show_all()
    while True:
        choice = input("Do you want to create another field? (y/n): ").strip().lower()
        if choice == "y":
            f_menu.create_field()
            f_menu.show_all()
        elif choice == "n":
            print("Exiting field menu.")
            break
        else:
            print("Invalid choice. Please enter 'y' or 'n'.")
