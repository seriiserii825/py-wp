import json
import os

from classes.acf.enum.EFieldType import EFieldType
from classes.acf.field.dto.FieldDTO import FieldDTO
from classes.acf.field.factories.FieldFactory import create_field
from classes.acf.field.factories.FieldTemplateFactory import FieldTemplateFactory
from classes.utils.Generate import Generate
from classes.utils.InputValidator import InputValidator
from classes.utils.Select import Select


class FieldMenu:
    def __init__(self, file_path: str):
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"The file '{file_path}' does not exist.")
        self.file_path = file_path

    def show_all(self):
        fields, _ = self._get_fields()
        for index, field_data in enumerate(fields):
            field = create_field(field_data)
            if field:
                field.print_field_with_subfields(index=index, indent=0)

    def create_field(self):
        fields, data = self._get_fields()

        field = self._input_field_metadata()
        new_field = FieldTemplateFactory.create(field)
        fields.append(new_field)

        self._save_data(data)

    def move_field(self):
        fields, _ = self._get_fields()

        if not fields:
            print("No fields available to move.")
            return

    def _input_field_metadata(self) -> FieldDTO:
        key = Generate.get_field_id()
        label = InputValidator.get_string("Enter field label: ")
        name = label.replace(" ", "_").lower()
        types = [ft.value for ft in EFieldType]
        selected_type = Select.select_one(types)

        required = InputValidator.get_bool(prompt="Field is required? (y/n): ")
        layout = self._determine_layout(selected_type)
        width = (
            InputValidator.get_int("Enter field width (0-100): ")
            if layout == "block" and self._is_simple_field(selected_type)
            else 100
        )

        return FieldDTO(
            key=key,
            label=label,
            name=name,
            type=selected_type,
            layout=layout,
            required=required,
            width=width,
        )

    def _determine_layout(self, field_type: str) -> str:
        if field_type == EFieldType.GROUP.value:
            layout = input("By default is block, type 'r' for row: ").strip()
            return "row" if layout == "r" else "block"
        print(f"Creating field of type: {field_type}")
        return "block"

    def _load_data(self) -> list:
        with open(self.file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save_data(self, data: list):
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    def _get_fields(self) -> tuple:
        data = self._load_data()
        parent = data[0]  # Assuming one section
        return parent.get("fields", []), data

    @staticmethod
    def _is_simple_field(field_type: str) -> bool:
        return field_type not in {
            EFieldType.GROUP.value,
            EFieldType.TAB.value,
        }
