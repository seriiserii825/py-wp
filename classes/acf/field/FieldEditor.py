from classes.acf.enum.EFieldType import EFieldType
from classes.utils.InputValidator import InputValidator
from classes.utils.Print import Print
from classes.utils.Select import Select


class FieldEditor:
    def __init__(self, repo, mover):
        self.repo = repo
        self.mover = mover

    def edit_field(self, data, fields):
        index_path = InputValidator.get_string("Enter field index (e.g. 1.2): ")
        target = self.mover.get_field_by_index(fields, index_path)
        if not isinstance(target, dict):
            Print.error("Invalid field at that index.")
            return

        while True:
            attributes = self.get_all_attributes(target)
            editable = self._get_editable(attributes)
            self._print_attributes(editable)

            selected = Select.select_one(list(editable.keys()))
            Print.info(f"Selected attribute: {selected}")

            if selected is None or selected == "exit":
                Print.info("Exiting edit mode.")
                return

            self._edit_attribute(selected, target)
            self.repo.save(data)
            Print.success("Field updated successfully.\n")

    def _get_editable(self, attrs):
        attrs = dict(attrs)
        attrs.pop("name", None)
        attrs["exit"] = "Exit edit mode"
        return attrs

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
        else:
            self._edit_generic(target, attr)

    def get_all_attributes(self, field):
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
        new_value = self._confirm("Is this field required? (y/n): ")
        target[attr] = 0 if not new_value else "true"

    def _edit_type(self, target):
        types = [ft.value for ft in EFieldType]
        selected_type = Select.select_one(types)
        if selected_type:
            target["type"] = selected_type

    def _edit_label(self, target):
        new_label = self.set_attribute_value("label")
        target_name = new_label.lower().replace(" ", "_")

        if target_name == target.get("name", ""):
            Print.error("Name already matches label, no change needed.")
            return

        target["name"] = target_name
        target["label"] = new_label

    def _edit_width(self, target):
        if "wrapper" not in target:
            target["wrapper"] = {}
        target["wrapper"]["width"] = self.set_attribute_value("width")

    def _edit_generic(self, target, attr):
        target[attr] = self.set_attribute_value(attr)

    def _edit_layout(self, target):
        types = ["block", "row"]
        selected_type = Select.select_one(types)
        if selected_type:
            target["layout"] = selected_type
