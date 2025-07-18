from dataclasses import dataclass


@dataclass
class FieldDTO:
    key: str
    label: str
    name: str
    type: str
    instructions: str = ""
    required: bool = False
    layout: str = "block"
    width: int = 100
