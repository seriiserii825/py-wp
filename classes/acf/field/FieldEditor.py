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

    def _edit_attribute(self, selected_attr, target):
        if selected_attr == "required":
            new_value = self._confirm("Is this field required? (y/n): ")
            target[selected_attr] = 0 if not new_value else "true"
        elif selected_attr == "type":
            types = [ft.value for ft in EFieldType]
            selected_type = Select.select_one(types)
            target["type"] = selected_type
        elif selected_attr == "label":
            target_name = (
                self.set_attribute_value(selected_attr).lower().replace(" ", "_")
            )
            if target_name == target["name"]:
                Print.error("Name already matches label, no change needed.")
                return
            else:
                target["name"] = (
                    self.set_attribute_value(selected_attr).lower().replace(" ", "_")
                )
            target["label"] = self.set_attribute_value(selected_attr)
        elif selected_attr == "width":
            if "wrapper" not in target:
                target["wrapper"] = {}
            target["wrapper"]["width"] = self.set_attribute_value(selected_attr)
        else:
            target[selected_attr] = self.set_attribute_value(selected_attr)

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
        if field.get("type") == "group":
            # add layout
            attributes["layout"] = field.get("layout", "")

        return attributes

    def _print_attributes(self, attrs):
        for k, v in attrs.items():
            print(f"{k}: {v}")
