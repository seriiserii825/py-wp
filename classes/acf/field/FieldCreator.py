from classes.acf.enum.EFieldType import EFieldType
from classes.acf.field.dto.FieldDTO import FieldDTO
from classes.acf.field.factories.FieldTemplateFactory import FieldTemplateFactory
from classes.utils.Generate import Generate
from classes.utils.InputValidator import InputValidator
from classes.utils.Select import Select


class FieldCreator:
    def create(self) -> dict:
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

        field = FieldDTO(
            key=key,
            label=label,
            name=name,
            type=selected_type,
            layout=layout,
            required=required,
            width=width,
        )

        return FieldTemplateFactory.create(field)

    def _determine_layout(self, field_type: str) -> str:
        if field_type == EFieldType.GROUP.value:
            layout = input("By default is block, type 'r' for row: ").strip()
            return "row" if layout == "r" else "block"
        print(f"Creating field of type: {field_type}")
        return "block"

    def _is_simple_field(self, field_type: str) -> bool:
        return field_type not in {
            EFieldType.GROUP.value,
            EFieldType.TAB.value,
        }
