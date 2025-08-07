from classes.files.FileCreatorFactory import FileCreatorFactory
from main_menu.file_type_menu import file_type_menu


def file_menu():
    file_type = file_type_menu()
    file = FileCreatorFactory.get_creator(file_type)
    file_path = file.create_file()
    file.template_to_file(file_path)
