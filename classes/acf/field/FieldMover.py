class FieldMover:
    @staticmethod
    def parse_index_path(index_str: str) -> list[int]:
        return [int(i) for i in index_str.split(".")]

    @staticmethod
    def get_field_container(fields, index_path, create=False):
        for idx in index_path[:-1]:
            field = fields[idx]
            if "sub_fields" not in field:
                if create:
                    field["sub_fields"] = []
                else:
                    raise KeyError(f"No sub_fields in field at index {idx}")
            fields = field["sub_fields"]
        return fields

    @classmethod
    def pop_field(cls, fields, index_path):
        parent = cls.get_field_container(fields, index_path)
        return parent.pop(index_path[-1])

    @classmethod
    def insert_field_into(cls, parent, index, field):
        parent.insert(index, field)

    def move_field(self, fields, source_str, dest_str):
        source = self.parse_index_path(source_str)
        dest = self.parse_index_path(dest_str)

        if source == dest:
            return  # nothing to do

        # Cache destination parent list before modifying the structure
        dest_parent = self.get_field_container(fields, dest, create=True)

        # Adjust destination index if necessary
        dest_index = dest[-1]
        if self._should_adjust_indices(source, dest):
            dest_index -= 1

        # Pop and insert
        field = self.pop_field(fields, source)
        self.insert_field_into(dest_parent, dest_index, field)

    def _should_adjust_indices(self, source, dest):
        return source[:-1] == dest[:-1] and source[-1] < dest[-1]

    @classmethod
    def get_field_by_index(cls, fields, index_str):
        index_path = cls.parse_index_path(index_str)
        parent = cls.get_field_container(fields, index_path)
        try:
            return parent[index_path[-1]]
        except IndexError:
            raise IndexError(f"Field at index '{index_str}' does not exist.")
