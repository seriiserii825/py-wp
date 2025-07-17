from classes.acf.field.FieldMenu import FieldMenu


def field_menu(section_file_json_path):
    f_menu = FieldMenu()
    f_menu.init(section_file_json_path)
    f_menu.show_all()
