from abc import ABC, abstractmethod


class Field(ABC):
    def __init__(self, field_data):
        self.key = field_data.get("key", "")
        self.label = field_data.get("label", "")
        self.name = field_data.get("name", "")
        self.type = field_data.get("type", "")
        self.instructions = field_data.get("instructions", "")
        self.required = field_data.get("required", False)
        self.width = field_data.get("wrapper", "")['width']

    def parse_fields(self, fields, parent_key):
        pass

    @abstractmethod
    def print_field(self, index, indent):
        pass

    def print_field_with_subfields(self, index, indent):
        self.print_field(index, indent)
