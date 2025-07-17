from acf.field.field_menu import field_menu
from classes.acf.section.SelectSection import SelectSection


def select_section():
    section = SelectSection.select_section()
    field_menu(section_file_json_path=section)
