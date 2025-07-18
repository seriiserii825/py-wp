class FieldMover:
    @staticmethod
    def parse_index_path(index_str: str) -> list[int]:
        return [int(i) for i in index_str.split(".")]

    @staticmethod
    def get_nested_field(fields, index_path):
        for idx in index_path[:-1]:
            fields = fields[idx].get("sub_fields", [])
        return fields

    @classmethod
    def pop_field(cls, fields, index_path):
        parent = cls.get_nested_field(fields, index_path)
        return parent.pop(index_path[-1])

    @classmethod
    def insert_field(cls, fields, index_path, field):
        parent = cls.get_nested_field(fields, index_path)
        parent.insert(index_path[-1], field)

    def move_field(self, fields, source_str, dest_str):
        source = self.parse_index_path(source_str)
        dest = self.parse_index_path(dest_str)
        field = self.pop_field(fields, source)
        self.insert_field(fields, dest, field)
