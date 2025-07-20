from classes.acf.field.factories.FieldFactory import create_field
from classes.acf.field.FieldCreator import FieldCreator
from classes.acf.field.FieldMover import FieldMover
from classes.acf.field.FieldRepository import FieldRepository
from classes.utils.InputValidator import InputValidator
from classes.utils.Print import Print
from classes.utils.Select import Select


class FieldMenu:
    def __init__(self, file_path: str):
        self.repo = FieldRepository(file_path)
        self.creator = FieldCreator()
        self.mover = FieldMover()

    def show_all(self):
        data = self.repo.load()
        fields = data[0].get("fields", [])
        for index, field_data in enumerate(fields):
            field = create_field(field_data)
            if field:
                field.print_field_with_subfields(index=index, indent=0)

    def move_after_create(self, fields: list, data):
        try:
            source_index = str(len(fields) - 1)
            dest = InputValidator.get_string("Enter destination index (e.g. 0.1): ")
            self.mover.move_field(fields, source_index, dest)
            self.repo.save(data)
            print("Field moved successfully.")
        except Exception as e:
            print(f"Error moving newly created field: {e}")

    def create_field(self):
        data = self.repo.load()
        fields = data[0].get("fields", [])

        new_field = self.creator.create()
        fields.append(new_field)

        self.move_after_create(fields, data)

        self.repo.save(data)
        print("Field created and saved.")

    def move_field(self):
        data = self.repo.load()
        fields = data[0].get("fields", [])

        if not fields:
            print("No fields to move.")
            return

        try:
            source = InputValidator.get_string("Enter source index (e.g. 1.2): ")
            dest = InputValidator.get_string("Enter destination index (e.g. 0.1): ")
            self.mover.move_field(fields, source, dest)
            self.repo.save(data)
            print("Field moved successfully.")
        except Exception as e:
            print(f"Error moving field: {e}")

    def edit_field(self):
        data = self.repo.load()
        fields = data[0].get("fields", [])

        if not fields:
            print("No fields to edit.")
            return

        try:
            index_path = InputValidator.get_string("Enter field index (e.g. 1.2): ")
            target = self.mover.get_field_by_index(fields, index_path)

            if not isinstance(target, dict):
                print("Invalid field at that index.")
                return

            field_attributes = self.get_all_field_attributes(target)

            while True:
                all_attributes = {
                    **field_attributes,
                    "exit": "Exit edit mode",
                }
                # remove name from the attributes to avoid confusion
                all_attributes = {
                    key: value for key, value in all_attributes.items() if key != "name"
                }

                self.print_field_attributes(all_attributes)

                selected_attr = Select.select_one(list(all_attributes.keys()))
                Print.info(f"Selected attribute: {selected_attr}")

                if selected_attr is None or selected_attr == "exit":
                    print("Exiting edit mode.")
                    return

                new_value = InputValidator.get_string(
                    f"Enter new value for '{selected_attr}': "
                )
                if selected_attr == "required":
                    new_value = new_value.lower() in ("true", "1", "yes")
                elif selected_attr == "label":
                    target_name = new_value.lower().replace(" ", "_")
                    if target_name == target["name"]:
                        Print.error("Name already matches label, no change needed.")
                        return
                    else:
                        target["name"] = new_value.lower().replace(" ", "_")
                    target["label"] = new_value
                elif selected_attr == "width":
                    if "wrapper" not in target:
                        target["wrapper"] = {}
                    target["wrapper"]["width"] = new_value
                else:
                    target[selected_attr] = new_value

                self.repo.save(data)
                Print.success("Field updated successfully.\n")

        except Exception as e:
            print(f"Error editing field: {e}")

    def get_all_field_attributes(self, field):
        attributes = {
            "key": field.get("key", ""),
            "label": field.get("label", ""),
            "name": field.get("name", ""),
            "type": field.get("type", ""),
            "instructions": field.get("instructions", ""),
            "required": field.get("required", False),
            "width": field.get("wrapper", {}).get("width", ""),
        }
        return attributes

    def print_field_attributes(self, field_attributes):
        for key, value in field_attributes.items():
            print(f"{key}: {value}")
        print("\n")
