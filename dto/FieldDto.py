from dataclasses import dataclass


@dataclass
class FieldDto:
    key: str
    label: str
    name: str
    type: str
    instructions: str = ""
    required: bool = False
