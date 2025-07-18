import json
import os

from classes.acf.field.FieldFactory import create_field


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
                field.print_field_with_subfields(color="blue", index=index, indent=0)
