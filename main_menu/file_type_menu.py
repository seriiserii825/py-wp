from classes.utils.ColorMenu import ColorMenu
from enum_folder.FileTypeEnum import FileTypeEnum


def file_type_menu() -> FileTypeEnum:
    rows = [
        f"[green]{FileTypeEnum.PHP.label} (php)",
        f"[blue]{FileTypeEnum.SCSS.label} (scss)",
        f"[green]{FileTypeEnum.PHPBlock.label} (phpb)",
        f"[green]{FileTypeEnum.PHPS.label} (php and css)",
        f"[green]{FileTypeEnum.PHPBS.label} (php and block and css)",
        f"[green]{FileTypeEnum.PHPP.label} (php page)",
        f"[green]{FileTypeEnum.PHPI.label} (php icon)",
        f"[yellow]{FileTypeEnum.JS.label} (js)",
        f"[green]{FileTypeEnum.PHPAPI.label} (php api)",
    ]

    choice = ColorMenu.select(rows, exit_label="[red]Back")
    if choice == 0:
        return FileTypeEnum.PHP
    if choice == 1:
        return FileTypeEnum.SCSS
    elif choice == 2:
        return FileTypeEnum.PHPBlock
    elif choice == 3:
        return FileTypeEnum.PHPS
    elif choice == 4:
        return FileTypeEnum.PHPBS
    elif choice == 5:
        return FileTypeEnum.PHPP
    elif choice == 6:
        return FileTypeEnum.PHPI
    elif choice == 7:
        return FileTypeEnum.JS
    elif choice == 8:
        return FileTypeEnum.PHPAPI
    elif choice == 9:
        return FileTypeEnum.NONE
    else:
        print("Invalid option. Please try again.")
        return file_type_menu()
