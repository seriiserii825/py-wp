from rich import print

from classes.acf.field.abc_dir.Field import Field


class GroupField(Field):
    def __init__(self, field_data):
        super().__init__(field_data)
        self.sub_fields = field_data.get("sub_fields", [])

    def print_field(self, index, indent=0):
        prefix = "--" * indent
        print(f"[yellow]{prefix}{index}) {self.label} - {self.name} - {self.type}")

    def parse_fields(self, fields, parent_key):
        return super().parse_fields(fields, parent_key)

    def print_field_with_subfields(self, index, indent=0):
        self.print_field(index, indent)

        from classes.acf.field.FieldFactory import create_field

        for i, sub_field_data in enumerate(self.sub_fields):
            sub_field = create_field(sub_field_data)
            if sub_field:
                sub_field.print_field_with_subfields(i, indent + 1)
