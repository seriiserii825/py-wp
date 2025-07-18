import json
import os

from classes.acf.enum.EFieldType import EFieldType
from classes.acf.field.FieldFactory import create_field
from classes.acf.field.FieldTemplateFactory import FieldTemplateFactory
from classes.acf.field.dto.FieldDTO import FieldDTO
from classes.utils.Generate import Generate
from classes.utils.InputValidator import InputValidator
from classes.utils.Select import Select


class FieldMenu:
    file_path = ""

    @classmethod
    def init(cls, section_file_json_path: str):
        cls.file_path = section_file_json_path
        if not os.path.exists(cls.file_path):
            raise FileNotFoundError(
                f"The file '{cls.file_path}' does not exist.")

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
        fields, data = FieldMenu._get_fields()
        field: FieldDTO
        field_key = Generate.get_field_id()
        field_label = InputValidator.get_string("Enter field label: ")
        field_name = field_label.replace(" ", "_").lower()
        field_types = [field_type.value for field_type in EFieldType]
        selected_type = Select.select_one(field_types)
        print("Field is required? (y/n): ", end="")
        field_required = InputValidator.get_bool()
        layout = "block"

        if selected_type == EFieldType.GROUP.value:
            layout = input("By default is block, type r for row").strip()
            if layout == "r":
                layout = "row"
        else:
            print(f"Creating field of type: {selected_type}")

        field = FieldDTO(
            key=field_key,
            label=field_label,
            name=field_name,
            type=selected_type,
            layout=layout,
            required=field_required,
        )
        new_field = FieldTemplateFactory.create(field)

        FieldMenu._write_to_file(fields, new_field, data)

    @staticmethod
    def _get_fields():
        with open(FieldMenu.file_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        parent = data[0]  # Assume one section for now
        fields = parent.get("fields", [])
        return (fields, data)

    @staticmethod
    def _write_to_file(fields, new_field, data):
        fields.append(new_field)
        with open(FieldMenu.file_path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)
