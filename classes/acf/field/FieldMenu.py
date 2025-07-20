from classes.acf.field.factories.FieldFactory import create_field
from classes.acf.field.FieldCreator import FieldCreator
from classes.acf.field.FieldMover import FieldMover
from classes.acf.field.FieldRepository import FieldRepository
from classes.utils.InputValidator import InputValidator


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
