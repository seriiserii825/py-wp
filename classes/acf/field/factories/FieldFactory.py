from classes.acf.field.fields_dir.FileField import FileField
from classes.acf.field.fields_dir.GalleryField import GalleryField
from classes.acf.field.fields_dir.GroupField import GroupField
from classes.acf.field.fields_dir.ImageField import ImageField
from classes.acf.field.fields_dir.MessageField import MessageField
from classes.acf.field.fields_dir.RepeaterField import RepeaterField
from classes.acf.field.fields_dir.TabField import TabField
from classes.acf.field.fields_dir.TextAreaField import TextAreaField
from classes.acf.field.fields_dir.TextField import TextField
from classes.acf.field.fields_dir.TrueFalse import TrueFalse
from classes.acf.field.fields_dir.WswgiEditorField import WswgiEditorField


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
        case "message":
            return MessageField(field_data)
        case _:
            print(f"Unsupported field type: {field_type}")
            return None
