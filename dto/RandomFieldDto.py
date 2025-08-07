from dataclasses import dataclass


@dataclass
class RandomFieldDto:
    name: str
    value: list[str]
