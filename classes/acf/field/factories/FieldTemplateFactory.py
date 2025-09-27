from classes.acf.enum.EFieldType import EFieldType
from classes.acf.field.dto.FieldDTO import FieldDTO


class FieldTemplateFactory:
    @staticmethod
    def create(dto: FieldDTO):
        base = {
            "key": dto.key,
            "label": dto.label,
            "name": dto.name,
            "aria-label": dto.aria_label,
            "type": dto.type,
            "instructions": dto.instructions,
            "required": dto.required,
            "conditional_logic": 0,
            "wrapper": {"width": dto.width, "class": "", "id": ""},
            "message": dto.message,
            "ui": dto.ui,
            "default_value": dto.default,
        }

        match dto.type:
            case EFieldType.GROUP.value:
                base["layout"] = dto.layout
                base["sub_fields"] = []
            case EFieldType.REPEATER.value:
                base["sub_fields"] = []
                base["layout"] = dto.layout
            case EFieldType.MESSAGE.value:
                base["message"] = dto.message
            case EFieldType.TRUE_FALSE.value:
                base["ui"] = dto.ui
                base["default_value"] = dto.default
            case EFieldType.GALLERY.value:
                base.update(
                    {
                        "return_format": "array"
                    }
                )
            case EFieldType.IMAGE.value:
                base.update(
                    {
                        "return_format": "array"
                    }
                )
            case EFieldType.TAB.value:
                base.update({"placement": "top", "endpoint": 0})
            # Add other types here

        return base
