from classes.acf.field.TextField import TextField
from classes.acf.field.TabField import TabField
from classes.acf.field.GroupField import GroupField
from classes.acf.field.GalleryField import GalleryField


def create_field(field_data):
    field_type = field_data.get("type")

    match field_type:
        case "text":
            return TextField(field_data)
        case "tab":
            return TabField(field_data)
        case "group":
            return GroupField(field_data)
        case "gallery":
            return GalleryField(field_data)
        case _:
            print(f"Unsupported field type: {field_type}")
            return None
