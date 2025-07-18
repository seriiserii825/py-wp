from classes.acf.field.FileField import FileField
from classes.acf.field.GalleryField import GalleryField
from classes.acf.field.GroupField import GroupField
from classes.acf.field.ImageField import ImageField
from classes.acf.field.RepeaterField import RepeaterField
from classes.acf.field.TabField import TabField
from classes.acf.field.TextAreaField import TextAreaField
from classes.acf.field.TextField import TextField
from classes.acf.field.TrueFalse import TrueFalse
from classes.acf.field.WswgiEditorField import WswgiEditorField


def create_field(field_data):
    field_type = field_data.get("type")

    match field_type:
        case "tab":
            return TabField(field_data)
        case "group":
            return GroupField(field_data)
        case "repeater":
            return RepeaterField(field_data)
        case "text":
            return TextField(field_data)
        case "textarea":
            return TextAreaField(field_data)
        case "wysiwyg":
            return WswgiEditorField(field_data)
        case "file":
            return FileField(field_data)
        case "image":
            return ImageField(field_data)
        case "gallery":
            return GalleryField(field_data)
        case "true_false":
            return TrueFalse(field_data)
        case _:
            print(f"Unsupported field type: {field_type}")
            return None
