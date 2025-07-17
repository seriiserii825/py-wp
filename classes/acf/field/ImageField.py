from classes.acf.field.Field import Field


class ImageField(Field):
    def parse_fields(self, fields, parent_key):
        pass

    def print_field(self, color, index, indent=0):
        print(f"[{index}] IMAGE FIELD - {self.label} (name: {self.name})")

    def print_field_with_subfields(self, color, index, indent=0):
        self.print_field(color, index)
