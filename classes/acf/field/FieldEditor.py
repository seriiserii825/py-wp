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
        # same logic from _handle_attribute_edit & sub-methods (can be copied in here)
        pass

    def get_all_attributes(self, field):
        return {
            "key": field.get("key", ""),
            "label": field.get("label", ""),
            "name": field.get("name", ""),
            "type": field.get("type", ""),
            "instructions": field.get("instructions", ""),
            "required": field.get("required", False),
            "width": field.get("wrapper", {}).get("width", ""),
        }

    def _print_attributes(self, attrs):
        for k, v in attrs.items():
            print(f"{k}: {v}")
