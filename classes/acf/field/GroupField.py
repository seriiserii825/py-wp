from classes.acf.field.Field import Field


class GroupField(Field):
    def __init__(self, field_data):
        super().__init__(field_data)
        self.sub_fields = field_data.get("sub_fields", [])

    def print_field(self, color, index, indent=0):
        prefix = "  " * indent
        print(f"{prefix}[{index}] 📦 GROUP - {self.label} (name: {self.name})")

    def parse_fields(self, fields, parent_key):
        return super().parse_fields(fields, parent_key)

    def print_field_with_subfields(self, color, index, indent=0):
        self.print_field(color, index, indent)

        from classes.acf.field.FieldFactory import create_field

        for i, sub_field_data in enumerate(self.sub_fields):
            sub_field = create_field(sub_field_data)
            if sub_field:
                sub_field.print_field_with_subfields(color, i + 1, indent + 1)
