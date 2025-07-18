from classes.acf.field.Field import Field

from rich import print


class TrueFalse(Field):
    def print_field(self, index, indent):
        prefix = " -- " * indent
        print(
            f"[green]{prefix}{index}) {self.label} - "
            f"{self.name} - {self.type} - {self.key}"
            f" - {self.instructions} - Required: {self.required} - Width: {self.width}"
        )
