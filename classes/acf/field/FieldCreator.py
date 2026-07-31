from classes.acf.enum.EFieldType import EFieldType
from classes.acf.field.FieldBuilder import FieldBuilder
from classes.acf.field.dto.FieldDTO import FieldDTO
from classes.acf.field.factories.FieldTemplateFactory import FieldTemplateFactory
from classes.utils.Generate import Generate


class FieldCreator:
    def __init__(self):
        self.builder = FieldBuilder()  # noqa: F821

    def ask_label_and_type(self) -> tuple[str, EFieldType]:
        label = self.builder.ask_label()
        selected_type = self.builder.ask_field_type()
        return label, selected_type

    def create(self, label: str, selected_type: EFieldType) -> dict | list[dict]:
        if selected_type == EFieldType.TAB:
            name = ""
        else:
            name = self.builder.label_to_name(label)
        key = Generate.get_field_id()

        if selected_type in {EFieldType.POST_OBJECT, EFieldType.PAGE_LINK}:
            post_type = self.builder.ask_post_type(selected_type)
        else:
            post_type = ""

        width = self.builder.ask_width(selected_type)
        layout = self.builder.ask_layout(selected_type)
        message = self.builder.ask_message(selected_type)
        ui = self.builder.ui_for_true_false(selected_type)
        default_value = self.builder.ask_default_value(selected_type)

        field = FieldDTO(
            key=key,
            label=label,
            name=name,
            aria_label="",
            type=selected_type,
            layout=layout,
            required=0,
            message=message,
            post_type=post_type,
            width=width,
            ui=ui,
            default=default_value,
        )

        if selected_type == EFieldType.TAB:
            return self.builder.handle_tab_field(field, label)

        return FieldTemplateFactory.create(field)
