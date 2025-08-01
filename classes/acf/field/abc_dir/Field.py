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
        self.ui = field_data.get("ui", 0)
        self.default_value = field_data.get("default_value", 0)

    def parse_fields(self, fields, parent_key):
        pass

    def print_field(self, index, indent):
        field_required = "[red]Required[/red]" if self.required else ""
        width = f"width: {self.width}" if {self.width} else ""
        prefix = " -- " * indent
        if self.type == "true_false":
            true_false_ui = "UI(1)" if self.ui else "UI(0)"
            default_value = "Default(1)" if self.default_value else "Default(0)"
        else:
            true_false_ui = ""
            default_value = ""

        print(
            f"[green]{prefix}{index}) {self.label} - {self.name} - [/green]"
            f"[blue]{self.type}(type)[/blue] - {self.key}"
            f" - {self.instructions} - {field_required} - {width}"
            f" - {true_false_ui if self.type == 'true_false' else ''}"
            f" - {default_value if self.type == 'true_false' else ''}"
        )

    def print_field_with_subfields(self, index, indent):
        self.print_field(index, indent)
