from classes.backup.Backup import Backup
from classes.utils.Menu import Menu
from main_menu.check_for_base_plugins import check_for_base_plugins


def backup_menu():
    check_for_base_plugins()

    menu_header = ["Index", "Action"]
    menu_colors = {
        "1": "green",
        "2": "yellow",
        "2.1": "yellow",
        "2.2": "yellow",
        "3": "blue",
        "4": "blue",
        "5": "blue",
        "5.1": "red",
        "6": "red",
    }
    menu_items = [
        ["1", "List Backups"],
        ["2", "Create Backup"],
        ["2.1", "Create and Copy to Mount"],
        ["2.2", "Create Backup on Server"],
        ["3", "Restore Backup"],
        ["4", "Restore from Downloads"],
        ["5", "Restore in Browser"],
        ["5.1", "Delete in Browser"],
        ["6", "Exit"],
    ]

    Menu.display(
        title="Backup Menu",
        columns=menu_header,
        rows=menu_items,
        row_styles=menu_colors,
    )

    choice = Menu.choose_option()
    if choice == 1:
        print("Listing backups...")
        bc = Backup()
        bc.listBackup()
    elif choice == 2:
        print("Creating backup...")
        bc = Backup()
        bc.makeBackup()
        # Call the function to create a backup
    elif choice == 2.1:
        print("Creating backup and copying to mount...")
        bc = Backup()
        bc.makeBackupInChrome()
