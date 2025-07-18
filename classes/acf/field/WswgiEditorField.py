from classes.acf.field.Field import Field

from rich import print


class WswgiEditorField(Field):
    def parse_fields(self, fields, parent_key):
        pass  # No subfields for basic text

    def print_field(self, color, index, indent):
        prefix = " -- " * indent
        print(
            f"[green]{prefix}{index}) {self.label} - "
            f"{self.name} - {self.type} - {self.key}"
        )

    def print_field_with_subfields(self, color, index, indent):
        self.print_field(color, index, indent)
