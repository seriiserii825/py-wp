from classes.acf.enum.EFieldType import EFieldType
from classes.acf.field.FieldBuilder import FieldBuilder
from classes.utils.InputValidator import InputValidator
from classes.utils.Print import Print
from classes.utils.Select import Select


class FieldEditor:
    def __init__(self, repo, mover):
        self.repo = repo
        self.mover = mover
        self.builder = FieldBuilder()

    def edit_field(self, data, fields):
        index_path = InputValidator.get_string("Enter field index (e.g. 1.2): ")
        try:
            target = self.mover.get_field_by_index(fields, index_path)
        except (IndexError, ValueError, KeyError) as e:
            Print.error(f"Invalid index '{index_path}': {e}")
            return

        if not isinstance(target, dict):
            Print.error("Invalid field at that index.")
            return

        parsed_path = self.mover.parse_index_path(index_path)
        inside_repeater = self.mover.is_path_inside_repeater(fields, parsed_path)

        while True:
            attributes = self.get_all_attributes(target, inside_repeater)
            editable = self._get_editable(attributes)
            editable["back"] = "Back"
            self._print_attributes(editable)

            selected = Select.select_with_fzf(list(editable.keys()))[0]
            Print.info(f"Selected attribute: {selected}")

            if selected is None or selected == "exit":
                Print.info("Exiting edit mode.")
                return

            if selected == "back":
                Print.info("Going back to main menu.\n")
                return

            self._edit_attribute(selected, target)
            self.repo.save(data)
            Print.success("Field updated successfully.\n")

    def _get_editable(self, attrs):
        attrs = dict(attrs)
        attrs.pop("name", None)
        attrs["exit"] = "Exit edit mode"
        return attrs

    def _type_enum(self, target) -> EFieldType:
        return EFieldType(target["type"])

    def _edit_attribute(self, attr, target):
        if attr == "required":
            self._edit_required(target, attr)
        elif attr == "type":
            self._edit_type(target)
        elif attr == "label":
            self._edit_label(target)
        elif attr == "width":
            self._edit_width(target)
        elif attr == "layout":
            self._edit_layout(target)
        elif attr == "ui":
            field_type = self._type_enum(target)
            target[attr] = self.builder.ui_for_true_false(field_type)
        elif attr == "default_value":
            field_type = self._type_enum(target)
            target[attr] = self.builder.ask_default_value(field_type)
        else:
            self._edit_generic(target, attr)

    def get_all_attributes(self, field, inside_repeater: bool = False):
        attributes = {
            "key": field.get("key", ""),
            "label": field.get("label", ""),
            "name": field.get("name", ""),
            "type": field.get("type", ""),
            "instructions": field.get("instructions", ""),
            "required": field.get("required", False),
            "width": field.get("wrapper", {}).get("width", ""),
        }
        if field.get("type") == "group" or field.get("type") == "repeater":
            attributes["layout"] = field.get("layout", "")

        if field.get("type") == "true_false":
            attributes["ui"] = field.get("ui", 0)
            if not inside_repeater:
                attributes["default_value"] = field.get("default_value", 0)
        elif field.get("type") in {"text", "textarea", "number"} and not inside_repeater:
            attributes["default_value"] = field.get("default_value", "")

        return attributes

    def _print_attributes(self, attrs):
        for k, v in attrs.items():
            print(f"{k}: {v}")

    def set_attribute_value(self, selected_attr) -> str:
        new_value = InputValidator.get_string(
            f"Enter new value for '{selected_attr}': "
        )
        return new_value.strip()

    def _check_field_is_empty(self, fields: list):
        if not fields:
            print("No fields to move.")
            return

    def _confirm(self, message: str) -> bool:
        return InputValidator.get_bool(message)

    def _edit_required(self, target, attr):
        new_value = self.builder.ask_required(self._type_enum(target))
        target[attr] = 0 if not new_value else "true"

    def _edit_type(self, target):
        new_type = self.builder.ask_field_type()
        target["type"] = new_type.value

    def _edit_label(self, target):
        new_label = self.builder.ask_label()
        new_name = self.builder.label_to_name(new_label)
        target["label"] = new_label
        target["name"] = new_name

    def _edit_width(self, target):
        width = self.builder.ask_width(self._type_enum(target))
        target.setdefault("wrapper", {})["width"] = width

    def _edit_generic(self, target, attr):
        target[attr] = self.set_attribute_value(attr)

    def _edit_layout(self, target):
        layout = self.builder.ask_layout(self._type_enum(target))
        target["layout"] = layout
