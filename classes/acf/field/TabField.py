from classes.acf.field.Field import Field


class TabField(Field):
    def parse_fields(self, fields, parent_key):
        pass  # No subfields

    def print_field(self, color, index, indent=0):
        print(f"[{index}] 📑 TAB - {self.label}")

    def print_field_with_subfields(self, color, index, indent=0):
        self.print_field(color, index)
