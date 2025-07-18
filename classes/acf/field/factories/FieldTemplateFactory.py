# classes/acf/field/FieldTemplateFactory.py

from classes.acf.enum.EFieldType import EFieldType
from classes.acf.field.dto.FieldDTO import FieldDTO


class FieldTemplateFactory:
    @staticmethod
    def create(dto: FieldDTO):
        base = {
            "key": dto.key,
            "label": dto.label,
            "name": dto.name,
            "type": dto.type,
            "instructions": dto.instructions,
            "required": dto.required,
            "conditional_logic": 0,
            "wrapper": {"width": dto.width, "class": "", "id": ""},
        }

        match dto.type:
            case EFieldType.GROUP.value:
                base["layout"] = dto.layout
                base["sub_fields"] = []
            case EFieldType.GALLERY.value:
                base.update(
                    {
                        "return_format": "url",
                        "library": "all",
                        "min": "",
                        "max": "",
                        "min_width": "",
                        "min_height": "",
                        "min_size": "",
                        "max_width": "",
                        "max_height": "",
                        "max_size": "",
                        "mime_types": "",
                        "insert": "append",
                        "preview_size": "thumbnail",
                    }
                )
            case EFieldType.TAB.value:
                base.update({"placement": "top", "endpoint": 0})
            # Add other types here

        return base
