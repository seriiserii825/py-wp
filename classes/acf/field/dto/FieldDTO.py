from dataclasses import dataclass, field


@dataclass
class FieldDTO:
    key: str
    label: str
    name: str
    type: str
    instructions: str = ""
    required: int | bool = 0
    layout: str = "block"
    width: int = 100
    message: str = ""
    ui: int = 0
    default: int = 0
    aria_label: str = field(default="", metadata={"alias": "aria-label"})
