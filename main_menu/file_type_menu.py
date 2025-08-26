from classes.utils.Menu import Menu
from enum_folder.FileTypeEnum import FileTypeEnum


def file_type_menu() -> FileTypeEnum:
    rows = [
        FileTypeEnum.PHP.label,
        f"{FileTypeEnum.PHPS.label} (php and scss)",
        f"{FileTypeEnum.PHPP.label} (php page)",
        f"{FileTypeEnum.PHPI.label} (php icon)",
        f"{FileTypeEnum.SCSS.label} (scss)",
        f"{FileTypeEnum.JS.label} (js)",
    ]

    choice = Menu.select_with_fzf(rows)
    if choice == 0:
        return FileTypeEnum.PHP
    elif choice == 1:
        return FileTypeEnum.PHPS
    elif choice == 2:
        return FileTypeEnum.PHPP
    elif choice == 3:
        return FileTypeEnum.PHPI
    elif choice == 4:
        return FileTypeEnum.SCSS
    elif choice == 5:
        return FileTypeEnum.JS
    else:
        print("Invalid option. Please try again.")
        return file_type_menu()
