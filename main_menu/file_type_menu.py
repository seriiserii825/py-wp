from classes.utils.Menu import Menu
from enum_folder.FileTypeEnum import FileTypeEnum


def file_type_menu() -> FileTypeEnum:
    headers = ["Index", "File Type"]
    row_styles = {
        0: "bold yellow",
        1: "bold yellow",
        2: "bold yellow",
        3: "bold yellow",
        4: "bold yellow",
        5: "bold blue",
        6: "bold red",
    }
    rows = [
        ["0", FileTypeEnum.PHP.value],
        ["1", f"{FileTypeEnum.PHPS.value} (php and scss)"],
        ["2", f"{FileTypeEnum.PHPC.value} (php component)"],
        ["3", f"{FileTypeEnum.PHPP.value} (php page)"],
        ["4", f"{FileTypeEnum.PHPI.value} (php icon)"],
        ["5", f"{FileTypeEnum.SCSS.value} (scss)"],
        ["6", f"{FileTypeEnum.JS.value} (js)"],
    ]
    Menu.display("File Type Menu", headers, rows, row_styles=row_styles)

    choice = Menu.choose_option()
    if choice == 0:
        return FileTypeEnum.PHP
    elif choice == 1:
        return FileTypeEnum.PHPS
    elif choice == 2:
        return FileTypeEnum.PHPC
    elif choice == 3:
        return FileTypeEnum.PHPP
    elif choice == 4:
        return FileTypeEnum.PHPI
    elif choice == 5:
        return FileTypeEnum.SCSS
    elif choice == 6:
        return FileTypeEnum.JS
    else:
        print("Invalid option. Please try again.")
        return file_type_menu()
