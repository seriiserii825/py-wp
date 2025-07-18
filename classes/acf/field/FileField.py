from classes.acf.field.Field import Field

from rich import print


class FileField(Field):
    def parse_fields(self, fields, parent_key):
        pass

    def print_field(self, index, indent):
        prefix = " -- " * indent
        print(
            f"[green]{prefix}{index}) {self.label} - "
            f"{self.name} - {self.type} - {self.key}"
        )

    def print_field_with_subfields(self, index, indent):
        self.print_field(index, indent)
