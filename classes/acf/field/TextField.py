from rich import print

from classes.acf.field.abc_dir.Field import Field


class TextField(Field):
    def print_field(self, index, indent):
        prefix = " -- " * indent
        print(
            f"[green]{prefix}{index}) {self.label} - "
            f"{self.name} - {self.type} - {self.key}"
            f" - {self.instructions} - Required: {self.required} - Width: {self.width}"
        )
