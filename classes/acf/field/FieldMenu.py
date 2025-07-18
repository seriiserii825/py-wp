import json
import os

from classes.acf.enum.EFieldType import EFieldType
from classes.acf.field.FieldFactory import create_field
from classes.utils.Generate import Generate
from classes.utils.InputValidator import InputValidator
from classes.utils.Select import Select


class FieldMenu:
    file_path = ""

    @classmethod
    def init(cls, section_file_json_path: str):
        cls.file_path = section_file_json_path
        if not os.path.exists(cls.file_path):
            raise FileNotFoundError(f"The file '{cls.file_path}' does not exist.")

    @staticmethod
    def show_all():
        with open(FieldMenu.file_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        fields = data[0].get("fields", [])
        for index, field_data in enumerate(fields):
            field = create_field(field_data)
            if field:
                field.print_field_with_subfields(index=index, indent=0)

    @staticmethod
    def create_field():
        field_key = Generate.get_field_id()
        field_label = InputValidator.get_string("Enter field label: ")
        field_name = field_label.replace(" ", "_").lower()
        field_types = [field_type.value for field_type in EFieldType]
        selected_type = Select.select_one(field_types)
        if selected_type == EFieldType.TAB.value:
            print(
                "Tab fields cannot be created directly. Please create a group field instead."
            )
        else:
            print(
                f"Creating field with key: {field_key}, label: {field_label}, name: {field_name}, type: {selected_type}"
            )
