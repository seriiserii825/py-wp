from main_menu.file_type_menu import file_type_menu


def file_menu():
    file_type = file_type_menu()
    print(f"file_type: {file_type.value}")
