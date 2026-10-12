from enum_folder.FileTypeEnum import FileTypeEnum
from main_menu.table_menu import BACK, table_menu

FILE_TYPES = [
    (FileTypeEnum.PHP, "php"),
    (FileTypeEnum.SCSS, "scss"),
    (FileTypeEnum.PHPBlock, "phpb"),
    (FileTypeEnum.PHPS, "php and css"),
    (FileTypeEnum.PHPBS, "php and block and css"),
    (FileTypeEnum.PHPP, "php page"),
    (FileTypeEnum.PHPI, "php icon"),
    (FileTypeEnum.SVGI, "svg icon"),
    (FileTypeEnum.JS, "js"),
    (FileTypeEnum.PHPAPI, "php api"),
]


def file_type_menu() -> FileTypeEnum:
    """Picked file type; FileTypeEnum.NONE on Back."""
    choice = table_menu(
        "File type", [f"{t.label} ({hint})" for t, hint in FILE_TYPES]
    )
    if choice == BACK:
        return FileTypeEnum.NONE
    return FILE_TYPES[choice][0]
