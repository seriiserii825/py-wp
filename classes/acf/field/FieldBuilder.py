from classes.acf.enum.EFieldType import EFieldType
from classes.acf.field.dto.FieldDTO import FieldDTO
from classes.acf.field.factories.FieldTemplateFactory import FieldTemplateFactory
from classes.utils.Generate import Generate
from classes.utils.InputValidator import InputValidator
from classes.utils.Select import Select


class FieldBuilder:
    DEFAULT_WIDTH = 100

    def ask_label(self) -> str:
        return InputValidator.get_string("Enter field label: ")

    def label_to_name(self, label: str) -> str:
        return label.replace(" ", "_").lower()

    def ask_field_type(self) -> str:
        types = [ft.value for ft in EFieldType]
        choice = Select.select_with_fzf(types)
        return choice[0]

    def ask_required(self, field_type: str) -> int | bool:
        if self.is_simple_field(field_type):
            bool_result = InputValidator.get_bool_true_default(
                "Is required, for no type 'n', 'y' by default: ")
            return True if bool_result else 0
        return 0

    def ask_width(self, field_type: str) -> int:
        if not self.is_simple_field(field_type):
            return self.DEFAULT_WIDTH
        raw = input("Enter field width (0-100), by default is 100: ").strip()
        return int(raw) if raw.isdigit() else self.DEFAULT_WIDTH

    def ask_message(self, field_type: str) -> str:
        if field_type == EFieldType.MESSAGE.value:
            return InputValidator.get_string("Enter message text: ")
        return ""

    def ask_layout(self, field_type: str) -> str:
        if field_type in {EFieldType.GROUP.value, EFieldType.REPEATER.value}:
            layout = input("By default is block, type 'r' for row: ").strip()
            return "row" if layout.lower() == "r" else "block"
        return "block"

    def ask_ui(self, field_type: str) -> int:
        if field_type == EFieldType.TRUE_FALSE.value:
            return (
                1
                if InputValidator.get_bool(
                    "Do you want to have UI for this field? (y/n): "
                )
                else 0
            )
        return 0

    def is_simple_field(self, field_type: str) -> bool:
        return field_type not in {
            EFieldType.GROUP.value,
            EFieldType.TAB.value,
            EFieldType.REPEATER.value,
        }

    def handle_tab_field(self, field: FieldDTO, label: str) -> list[dict]:
        tab_field = FieldTemplateFactory.create(field)
        if InputValidator.get_bool(
            "Do you want to create a group with the same label inside this tab? (y/n): "
        ):
            print("Creating group under the tab...")
            group_field = self.create_group(label)
            return [group_field, tab_field]
        return [tab_field]

    def create_group(self, label: str) -> dict:
        key = Generate.get_field_id()
        name = self.label_to_name(label)
        layout = self.determine_layout(EFieldType.GROUP.value)

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

    def determine_layout(self, field_type: str) -> str:
        if field_type in {EFieldType.GROUP.value, EFieldType.REPEATER.value}:
            layout = input("By default is block, type 'r' for row: ").strip()
            return "row" if layout.lower() == "r" else "block"
        return "block"

    def ui_for_true_false(self, field_type: str) -> int:
        if field_type == EFieldType.TRUE_FALSE.value:
            return (
                1
                if InputValidator.get_bool(
                    "Do you want to have UI for this field? (y/n): "
                )
                else 0
            )
        return 0

    def default_value_for_true_false(self, field_type: str) -> int:
        if field_type == EFieldType.TRUE_FALSE.value:
            return (
                1
                if InputValidator.get_bool(
                    "Do you want to set default value for this field? (y/n): "
                )
                else 0
            )
        return 0
