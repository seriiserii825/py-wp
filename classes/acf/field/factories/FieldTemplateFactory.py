from typing import Any

from classes.acf.enum.EFieldType import EFieldType
from classes.acf.field.dto.FieldDTO import FieldDTO


class FieldTemplateFactory:
    @staticmethod
    def create(dto: FieldDTO):
        base: dict[str, Any] = {
            "key": dto.key,
            "label": dto.label,
            "name": dto.name,
            "aria-label": dto.aria_label,
            "type": dto.type.value,
            "post_type": dto.post_type,
            "instructions": dto.instructions,
            "required": dto.required,
            "conditional_logic": 0,
            "wrapper": {"width": dto.width, "class": "", "id": ""},
            "message": dto.message,
            "ui": dto.ui,
            "default_value": dto.default,
        }

        match dto.type:
            case EFieldType.GROUP:
                base["layout"] = dto.layout
                base["sub_fields"] = []
            case EFieldType.REPEATER:
                base["sub_fields"] = []
                base["layout"] = dto.layout
            case EFieldType.MESSAGE:
                base["message"] = dto.message
            case EFieldType.TRUE_FALSE:
                base["ui"] = dto.ui
                base["default_value"] = dto.default
            case EFieldType.GALLERY:
                base.update({"return_format": "array"})
            case EFieldType.IMAGE:
                base.update({"return_format": "array"})
            case EFieldType.POST_OBJECT:
                base.update({"return_format": "id"})
            case EFieldType.TAB:
                base.update({"placement": "top", "endpoint": 0})
            # Add other types here

        return base
