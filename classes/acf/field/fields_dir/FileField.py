from classes.acf.field.abc_dir.Field import Field


class FileField(Field):
    def parse_fields(self, fields, parent_key):
        pass

    def print_field_with_subfields(self, index, indent):
        self.print_field(index, indent)
