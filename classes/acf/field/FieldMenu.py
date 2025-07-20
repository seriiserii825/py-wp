from classes.acf.enum.EFieldType import EFieldType
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
        _, fields = self._load_fields()
        for index, field_data in enumerate(fields):
            field = create_field(field_data)
            if field:
                field.print_field_with_subfields(index=index, indent=0)

    def create_field(self):
        data, fields = self._load_fields()

        new_field = self.creator.create()
        fields.append(new_field)

        self._move_after_create(fields, data)

        self.repo.save(data)
        print("Field created and saved.")

    def _move_after_create(self, fields: list, data):
        try:
            source_index = str(len(fields) - 1)
            dest = InputValidator.get_string("Enter destination index (e.g. 0.1): ")
            self.mover.move_field(fields, source_index, dest)
            self.repo.save(data)
            print("Field moved successfully.")
        except Exception as e:
            print(f"Error moving newly created field: {e}")

    def move_field(self):
        data, fields = self._load_fields()

        self._check_field_is_empty(fields)

        try:
            source = InputValidator.get_string("Enter source index (e.g. 1.2): ")
            dest = InputValidator.get_string("Enter destination index (e.g. 0.1): ")
            self.mover.move_field(fields, source, dest)
            self.repo.save(data)
            print("Field moved successfully.")
        except Exception as e:
            print(f"Error moving field: {e}")

    def edit_field(self):
        data, fields = self._load_fields()

        self._check_field_is_empty(fields)

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

                if selected_attr == "required":
                    new_value = self._confirm("Is this field required? (y/n): ")
                    target[selected_attr] = 0 if not new_value else "true"
                elif selected_attr == "type":
                    types = [ft.value for ft in EFieldType]
                    selected_type = Select.select_one(types)
                    target["type"] = selected_type
                elif selected_attr == "label":
                    target_name = (
                        self.set_attribute_value(selected_attr)
                        .lower()
                        .replace(" ", "_")
                    )
                    if target_name == target["name"]:
                        Print.error("Name already matches label, no change needed.")
                        return
                    else:
                        target["name"] = (
                            self.set_attribute_value(selected_attr)
                            .lower()
                            .replace(" ", "_")
                        )
                    target["label"] = self.set_attribute_value(selected_attr)
                elif selected_attr == "width":
                    if "wrapper" not in target:
                        target["wrapper"] = {}
                    target["wrapper"]["width"] = self.set_attribute_value(selected_attr)
                else:
                    target[selected_attr] = self.set_attribute_value(selected_attr)

                self.repo.save(data)
                Print.success("Field updated successfully.\n")

        except Exception as e:
            print(f"Error editing field: {e}")

    def delete_field(self):
        data, fields = self._load_fields()

        self._check_field_is_empty(fields)

        try:
            index_path_str = "Enter field index to delete (e.g. 1.2): "
            print("Calling _get_index_path...")
            index_path = self._get_index_path(index_path_str)
            print(f"Got index_path: {index_path}")

            confirm = self._confirm(
                "Are you sure you want to delete field at index"
                f" '{index_path}'? (y/n): "
            )
            if not confirm:
                print("Delete cancelled.")
                return

            deleted_field = self.mover.pop_field(fields, index_path)

            Print.success(
                "Deleted field: "
                f"{deleted_field.get('label', deleted_field.get('name', 'Unnamed'))}"
            )

            self.repo.save(data)
            Print.success("Field deleted and saved.")

        except IndexError:
            Print.error("Invalid index. No field deleted.")
        except Exception as e:
            Print.error(f"Error deleting field: {e}")

    def delete_fields(self):
        data, fields = self._load_fields()

        self._check_field_is_empty(fields)

        try:
            index_path_input = InputValidator.get_string(
                "Enter field indices to delete (comma-separated, "
                "from bigger to smaller,"
                "e.g. 3.2,3.1,3.0): "
            )
            index_path_strs = [
                s.strip() for s in index_path_input.split(",") if s.strip()
            ]

            index_paths = [self.mover.parse_index_path(s) for s in index_path_strs]

            if not index_paths:
                Print.error("No valid indices provided.")
                return

            # --- Check for prefix conflicts (e.g. 3 and 3.2) ---
            def is_prefix(shorter, longer):
                return len(shorter) < len(longer) and longer[: len(shorter)] == shorter

            for i, path1 in enumerate(index_paths):
                for j, path2 in enumerate(index_paths):
                    if i != j and (is_prefix(path1, path2) or is_prefix(path2, path1)):
                        Print.error(
                            f"Invalid index combination: "
                            f"{'.'.join(map(str, path1))}"
                            f" and {'.'.join(map(str, path2))} "
                            f"cannot be deleted together."
                        )
                        return

            confirm = self._confirm(
                "Are you sure you want to delete these"
                f" {len(index_paths)} field(s)? (y/n): "
            )
            if not confirm:
                print("Delete cancelled.")
                return

            index_paths.sort(reverse=True)  # Delete from deepest first

            for path in index_paths:
                try:
                    deleted_field = self.mover.pop_field(fields, path)
                    label = deleted_field.get(
                        "label", deleted_field.get("name", "Unnamed")
                    )
                    Print.success(
                        f"Deleted: {label} at index {'.'.join(map(str, path))}"
                    )
                except Exception as e:
                    Print.error(
                        f"Failed to delete at index {'.'.join(map(str, path))}: {e}"
                    )

            self.repo.save(data)
            Print.success("All selected fields deleted and saved.")

        except Exception as e:
            Print.error(f"Error during deletion: {e}")

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

    def _load_fields(self):
        data = self.repo.load()
        return data, data[0].get("fields", [])

    def print_field_attributes(self, field_attributes):
        for key, value in field_attributes.items():
            print(f"{key}: {value}")
        print("\n")

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

    def _get_index_path(self, prompt: str) -> list:
        index_str = InputValidator.get_string(prompt)
        print(f"index_str: {index_str}")
        return self.mover.parse_index_path(index_str)
