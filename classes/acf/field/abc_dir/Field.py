from abc import ABC

from rich import print


class Field(ABC):
    def __init__(self, field_data):
        self.key = field_data.get("key", "")
        self.label = field_data.get("label", "")
        self.name = field_data.get("name", "")
        self.type = field_data.get("type", "")
        self.instructions = field_data.get("instructions", "")
        self.required = field_data.get("required", False)
        self.width = field_data.get("wrapper", "")["width"]
        self.layout = field_data.get("layout", "group")

    def parse_fields(self, fields, parent_key):
        pass

    def print_field(self, index, indent):
        field_required = "[red]Required[/red]" if self.required else ""
        width = f"width: {self.width}" if {self.width} else ""
        prefix = " -- " * indent
        print(
            f"[green]{prefix}{index}) {self.label} - {self.name} - [/green]"
            f"[blue]{self.type}(type)[/blue] - {self.key}"
            f" - {self.instructions} - {field_required} - {width}"
        )

    def print_field_with_subfields(self, index, indent):
        self.print_field(index, indent)
