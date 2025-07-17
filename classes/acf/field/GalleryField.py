from classes.acf.field.Field import Field

class GalleryField(Field):
    def parse_fields(self, fields, parent_key):
        pass

    def print_field(self, color, index):
        print(f"[{index}] 🖼️ GALLERY - {self.label} (name: {self.name})")

    def print_field_with_subfields(self, color, index):
        self.print_field(color, index)
