from dataclasses import dataclass


@dataclass
class FormFieldsDto:
    all_fields: list[str]
    required_fields: list[str]
