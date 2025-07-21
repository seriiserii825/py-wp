from enum import Enum


class EFieldType(Enum):
    TEXT = "text"
    TEXTAREA = "textarea"
    WYSIWYG = "wysiwyg"
    IMAGE = "image"
    GALLERY = "gallery"
    FILE = "file"
    TRUE_FALSE = "true_false"
    TAB = "tab"
    GROUP = "group"
    REPEATER = "repeater"
    MESSAGE = "message"
