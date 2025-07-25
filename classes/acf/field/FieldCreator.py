from classes.acf.enum.EFieldType import EFieldType
from classes.acf.field.dto.FieldDTO import FieldDTO
from classes.acf.field.factories.FieldTemplateFactory import FieldTemplateFactory
from classes.utils.Generate import Generate
from classes.utils.InputValidator import InputValidator
from classes.utils.Select import Select


class FieldCreator:
    def create(self) -> dict | list[dict]:
        key = Generate.get_field_id()
        label = InputValidator.get_string("Enter field label: ")
        name = label.replace(" ", "_").lower()

        types = [ft.value for ft in EFieldType]
        selected_type = Select.select_one(types)

        if self._is_simple_field(selected_type):
            required = InputValidator.get_bool(prompt="Field is required? (y/n): ")
        else:
            required = False

        layout = self._determine_layout(selected_type)

        message = ""
        if selected_type == EFieldType.MESSAGE.value:
            message = InputValidator.get_string("Enter message text: ")

        raw = input("Enter field width (0-100), by default is 100: ")
        if not raw.strip():
            width = 100
        else:
            width = int(raw.strip())

        print(f"{layout}: layout")

        field = FieldDTO(
            key=key,
            label=label,
            name=name,
            type=selected_type,
            layout=layout,
            required=required,
            message=message,
            width=width,
        )

        if selected_type == EFieldType.TAB.value:
            tab_field = FieldTemplateFactory.create(field)
            want_group = InputValidator.get_bool(
                "Do you want to create a group "
                "with the same label inside this tab? (y/n): "
            )
            if want_group:
                print("Creating group under the tab...")
                group_field = self._create_group(label)
                return [group_field, tab_field]
            else:
                return [tab_field]

        return FieldTemplateFactory.create(field)

    def _create_group(self, label: str) -> dict:
        key = Generate.get_field_id()
        name = label.replace(" ", "_").lower()
        layout = self._determine_layout(EFieldType.GROUP.value)

        field = FieldDTO(
            key=key,
            label=label,
            name=name,
            type=EFieldType.GROUP.value,
            layout=layout,
            required=False,
            width=100,
        )
        return FieldTemplateFactory.create(field)

    def _determine_layout(self, field_type: str) -> str:
        if (
            field_type == EFieldType.GROUP.value
            or field_type == EFieldType.REPEATER.value
        ):
            layout = input("By default is block, type 'r' for row: ").strip()
            return "row" if layout == "r" else "block"
        return "block"

    def _is_simple_field(self, field_type: str) -> bool:
        return field_type not in {
            EFieldType.GROUP.value,
            EFieldType.TAB.value,
            EFieldType.REPEATER.value,
        }
