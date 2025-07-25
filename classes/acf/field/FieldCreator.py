from classes.acf.enum.EFieldType import EFieldType
from classes.acf.field.dto.FieldDTO import FieldDTO
from classes.acf.field.factories.FieldTemplateFactory import FieldTemplateFactory
from classes.utils.Generate import Generate
from classes.utils.InputValidator import InputValidator
from classes.utils.Select import Select


class FieldCreator:
    DEFAULT_WIDTH = 100

    def create(self) -> dict | list[dict]:
        label = self._get_label()
        name = self._label_to_name(label)
        key = Generate.get_field_id()
        selected_type = self._select_field_type()

        required = self._ask_if_required(selected_type)
        width = self._ask_field_width(selected_type)
        layout = self._determine_layout(selected_type)
        message = self._ask_message_if_needed(selected_type)

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
            return self._handle_tab_field(field, label)

        return FieldTemplateFactory.create(field)

    def _handle_tab_field(self, field: FieldDTO, label: str) -> list[dict]:
        tab_field = FieldTemplateFactory.create(field)
        if InputValidator.get_bool(
            "Do you want to create a group with the same label inside this tab? (y/n): "
        ):
            print("Creating group under the tab...")
            group_field = self._create_group(label)
            return [group_field, tab_field]
        return [tab_field]

    def _create_group(self, label: str) -> dict:
        key = Generate.get_field_id()
        name = self._label_to_name(label)
        layout = self._determine_layout(EFieldType.GROUP.value)

        field = FieldDTO(
            key=key,
            label=label,
            name=name,
            type=EFieldType.GROUP.value,
            layout=layout,
            required=False,
            width=self.DEFAULT_WIDTH,
        )
        return FieldTemplateFactory.create(field)

    def _get_label(self) -> str:
        return InputValidator.get_string("Enter field label: ")

    def _label_to_name(self, label: str) -> str:
        return label.replace(" ", "_").lower()

    def _select_field_type(self) -> str:
        types = [ft.value for ft in EFieldType]
        return Select.select_one(types)

    def _ask_if_required(self, field_type: str) -> bool:
        return (
            InputValidator.get_bool("Field is required? (y/n): ")
            if self._is_simple_field(field_type)
            else False
        )

    def _ask_field_width(self, field_type: str) -> int:
        if not self._is_simple_field(field_type):
            return self.DEFAULT_WIDTH
        raw = input("Enter field width (0-100), by default is 100: ").strip()
        return int(raw) if raw.isdigit() else self.DEFAULT_WIDTH

    def _ask_message_if_needed(self, field_type: str) -> str:
        if field_type == EFieldType.MESSAGE.value:
            return InputValidator.get_string("Enter message text: ")
        return ""

    def _determine_layout(self, field_type: str) -> str:
        if field_type in {EFieldType.GROUP.value, EFieldType.REPEATER.value}:
            layout = input("By default is block, type 'r' for row: ").strip()
            return "row" if layout.lower() == "r" else "block"
        return "block"

    def _is_simple_field(self, field_type: str) -> bool:
        return field_type not in {
            EFieldType.GROUP.value,
            EFieldType.TAB.value,
            EFieldType.REPEATER.value,
        }
