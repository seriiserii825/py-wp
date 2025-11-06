from classes.utils.Menu import Menu
from enum_folder.FileTypeEnum import FileTypeEnum


def file_type_menu() -> FileTypeEnum:
    rows = [
        f"0.{FileTypeEnum.PHP.label} (php)",
        f"1.{FileTypeEnum.PHPBlock.label} (phpb)",
        f"2.{FileTypeEnum.PHPS.label} (php and scss)",
        f"3.{FileTypeEnum.PHPP.label} (php page)",
        f"4.{FileTypeEnum.PHPI.label} (php icon)",
        f"5.{FileTypeEnum.SCSS.label} (scss)",
        f"6.{FileTypeEnum.JS.label} (js)",
        "7.Back",
    ]

    choice = Menu.select_fzf(rows)
    if choice == 0:
        return FileTypeEnum.PHP
    if choice == 1:
        return FileTypeEnum.PHPBlock
    elif choice == 2:
        return FileTypeEnum.PHPS
    elif choice == 3:
        return FileTypeEnum.PHPP
    elif choice == 4:
        return FileTypeEnum.PHPI
    elif choice == 5:
        return FileTypeEnum.SCSS
    elif choice == 6:
        return FileTypeEnum.JS
    elif choice == 7:
        return FileTypeEnum.NONE
    else:
        print("Invalid option. Please try again.")
        return file_type_menu()
