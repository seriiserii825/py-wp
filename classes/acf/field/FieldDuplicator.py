import copy

from classes.acf.field.FieldMover import FieldMover
from classes.acf.field.FieldRepository import FieldRepository
from classes.utils.Generate import Generate
from classes.utils.InputValidator import InputValidator


class FieldDuplicator:
    def __init__(self, repo: FieldRepository, mover: FieldMover):
        self.repo = repo
        self.mover = mover

    SEPARATOR = "|"

    def duplicate_field(self, data: list, fields: list):
        source_index = InputValidator.get_string("Enter source field index to duplicate (e.g. 0 or 1.2): ")
        field = self.mover.get_field_by_index(fields, source_index)

        raw = InputValidator.get_string(
            f"Enter new label(s), separate multiple with '{self.SEPARATOR}' "
            f"(original: {field.get('label', '')}): "
        )
        labels = [lbl.strip() for lbl in raw.split(self.SEPARATOR) if lbl.strip()]
        if not labels:
            print("No labels provided, aborting.")
            return

        after_original = InputValidator.get_bool("Place all new fields right after original? (y/n): ")
        if after_original:
            source_path = self.mover.parse_index_path(source_index)
            dest_parent = self.mover.get_field_container(fields, source_path)
            last = source_path[-1]
            insert_at = (last if last is not None else 0) + 1
        else:
            dest_index = InputValidator.get_string("Enter destination index (e.g. 0 or 1.): ")
            dest_path = self.mover.parse_index_path(dest_index)
            dest_parent = self.mover.get_field_container(fields, dest_path, create=True)
            insert_at = dest_path[-1] if dest_path[-1] is not None else len(dest_parent)

        for offset, label in enumerate(labels):
            name = label.replace(" ", "_").lower()
            duplicated = copy.deepcopy(field)
            duplicated["label"] = label
            duplicated["name"] = name
            self._regenerate_keys(duplicated)
            self.mover.insert_field_into(dest_parent, insert_at + offset, duplicated)
            print(f"  + '{label}' (name: {name})")

        self.repo.save(data)
        print(f"Done. {len(labels)} field(s) duplicated.")

    def _regenerate_keys(self, field: dict):
        field["key"] = Generate.get_field_id()
        for sub in field.get("sub_fields", []):
            self._regenerate_keys(sub)
