from classes.acf.field.factories.FieldFactory import create_field
from classes.acf.field.FieldCreator import FieldCreator
from classes.acf.field.FieldDeleter import FieldDeleter
from classes.acf.field.FieldEditor import FieldEditor
from classes.acf.field.FieldMover import FieldMover
from classes.acf.field.FieldRepository import FieldRepository
from classes.acf.field.GroupCopy import GroupCopy
from classes.utils.InputValidator import InputValidator


class FieldMenu:
    def __init__(self, file_path: str):
        self.repo = FieldRepository(file_path)
        self.creator = FieldCreator()
        self.mover = FieldMover()
        self.editor = FieldEditor(self.repo, self.mover)
        self.deleter = FieldDeleter(self.repo, self.mover)
        self.copy_group = GroupCopy(file_path)

    def show_all(self):
        _, fields = self._load_fields()
        for index, field_data in enumerate(fields):
            field = create_field(field_data)
            if field:
                field.print_field_with_subfields(index=index, indent=0)

    def show_only_tab_group(self, active_index: int = 0):
        _, fields = self._load_fields()
        for index, field_data in enumerate(fields):
            if field_data.get("type") not in ("tab", "group"):
                continue
            field = create_field(field_data)
            if field:
                if active_index == index:
                    field.print_field_with_subfields(index=index, indent=0)
                else:
                    field.print_field(index=index, indent=0, active=False)

    def select_tab_group_index(self) -> int | None:
        from classes.utils.Select import Select

        _, fields = self._load_fields()
        tab_groups = [
            (index, fd)
            for index, fd in enumerate(fields)
            if fd.get("type") in ("tab", "group")
        ]
        if not tab_groups:
            print("No tab/group fields found.")
            return None

        options = [
            f"{idx}) {fd.get('label', fd.get('name', '?'))} ({fd.get('type')})"
            for idx, fd in tab_groups
        ]
        selected = Select.select_with_fzf(options)
        if not selected or selected == [""]:
            return None

        pos = options.index(selected[0])
        return tab_groups[pos][0]

    def create_field(self):
        data, fields = self._load_fields()
        new_field = self.creator.create()
        if isinstance(new_field, list):
            fields.extend(new_field)
        else:
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

    def move_field(self) -> str:
        data, fields = self._load_fields()
        self._check_field_is_empty(fields)
        try:
            input_dest = InputValidator.get_string(
                "Enter source and dest separated by comma, 8,4: ",
                allow_empty=True,
            )
            source, dest = (s.strip() for s in input_dest.split(",")) if input_dest else (None, None)
            if not source:
                source = InputValidator.get_string("Enter source index (e.g. 0.1): ")
            if not dest:
                dest = InputValidator.get_string("Enter destination index (e.g. 0.1): ")
            self.mover.move_field(fields, source, dest)
            self.repo.save(data)
            print("Field moved successfully.")
            return dest
        except Exception as e:
            raise Exception(f"Error moving field: {e}")

    def edit_field(self):
        data, fields = self._load_fields()
        self._check_field_is_empty(fields)
        self.editor.edit_field(data, fields)

    def delete_field(self):
        data, fields = self._load_fields()
        self._check_field_is_empty(fields)
        self.deleter.delete_single(data, fields)

    def delete_fields(self):
        data, fields = self._load_fields()
        self._check_field_is_empty(fields)
        self.deleter.delete_multiple(data, fields)

    def copy_group_to_clipboard(self):
        _, fields = self._load_fields()
        self._check_field_is_empty(fields)
        try:
            source = InputValidator.get_string("Enter group index to copy (e.g. 1): ")
            self.copy_group.copy_to_clipboard(fields, source)
            print("Group copied to clipboard.")
        except Exception as e:
            print(f"Error copying group: {e}")

    def _load_fields(self):
        data = self.repo.load()
        return data, data[0].get("fields", [])

    def _check_field_is_empty(self, fields: list):
        if not fields:
            print("No fields to move.")
            return
