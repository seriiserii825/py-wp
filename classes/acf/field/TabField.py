from rich import print

from classes.acf.field.abc_dir.Field import Field


class TabField(Field):
    def print_field(self, index, indent=0):
        print(f"[blue]{index}) {self.label}")
