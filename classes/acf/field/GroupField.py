from classes.acf.field.Field import Field


class GroupField(Field):
    def __init__(self, field_data):
        super().__init__(field_data)
        self.sub_fields = field_data.get("sub_fields", [])

    def parse_fields(self, fields, parent_key):
        pass

    def print_field(self, color, index):
        print(f"[{index}] 📦 GROUP - {self.label} (name: {self.name})")

    def print_field_with_subfields(self, color, index):
        print()
        self.print_field(color, index)

        from classes.acf.field.FieldFactory import create_field  # 👈 move here
        for i, sub_field_data in enumerate(self.sub_fields):
            sub_field = create_field(sub_field_data)
            if sub_field:
                print(f"  └── Subfield {i + 1}:")
                sub_field.print_field_with_subfields(color, i + 1)
