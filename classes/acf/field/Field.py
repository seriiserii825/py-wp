from abc import ABC, abstractmethod


class Field(ABC):
    def __init__(self, field_data):
        self.key = field_data.get("key", "")
        self.label = field_data.get("label", "")
        self.name = field_data.get("name", "")
        self.type = field_data.get("type", "")
        self.instructions = field_data.get("instructions", "")
        self.required = field_data.get("required", False)

    @abstractmethod
    def parse_fields(self, fields, parent_key):
        pass

    @abstractmethod
    def print_field(self, color, index, indent):
        pass
