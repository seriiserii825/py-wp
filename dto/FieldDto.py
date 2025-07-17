
from dataclasses import dataclass
from typing import List


@dataclass
class FieldDto():
    key: str
    label: str
    name: str
    type: str
    instructions: str = ""
    required: bool = False
