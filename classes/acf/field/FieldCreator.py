from classes.acf.enum.EFieldType import EFieldType
from classes.acf.field.FieldBuilder import FieldBuilder
from classes.acf.field.dto.FieldDTO import FieldDTO
from classes.acf.field.factories.FieldTemplateFactory import FieldTemplateFactory
from classes.utils.Generate import Generate


class FieldCreator:
    def __init__(self):
        self.builder = FieldBuilder()  # noqa: F821

    def create(self) -> dict | list[dict]:
        label = self.builder.ask_label()
        name = self.builder.label_to_name(label)
        key = Generate.get_field_id()
        selected_type = self.builder.ask_field_type()

        required = self.builder.ask_required(selected_type)
        width = self.builder.ask_width(selected_type)
        layout = self.builder.ask_layout(selected_type)
        message = self.builder.ask_message(selected_type)
        ui = self.builder.ui_for_true_false(selected_type)
        true_false_default = self.builder.default_value_for_true_false(selected_type)

        field = FieldDTO(
            key=key,
            label=label,
            name=name,
            type=selected_type,
            layout=layout,
            required=required,
            message=message,
            width=width,
            ui=ui,
            default=true_false_default,
        )

        if selected_type == EFieldType.TAB.value:
            return self.builder.handle_tab_field(field, label)

        return FieldTemplateFactory.create(field)
