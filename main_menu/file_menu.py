from classes.files.FileCreatorFactory import FileCreatorFactory
from main_menu.file_type_menu import file_type_menu


def file_menu():
    file_type = file_type_menu()
    if file_type.name == "NONE":
        return
    file = FileCreatorFactory.get_creator(file_type)
    file_path = file.create_file(use_dir=file_type.use_dir)
    file.template_to_file(file_path)
