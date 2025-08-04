from classes.backup.Backup import Backup
from classes.utils.Menu import Menu
from main_menu.check_for_base_plugins import check_for_base_plugins


def backup_menu():
    check_for_base_plugins()

    menu_header = ["Index", "Action"]
    menu_colors = {
        "1": "green",
        "2": "yellow",
        "3": "yellow",
        "4": "yellow",
        "5": "blue",
        "6": "blue",
        "7": "blue",
        "8": "red",
        "9": "red",
    }
    menu_items = [
        ["1", "List Backups"],
        ["2", "Create Backup"],
        ["3", "Create and Copy to Mount"],
        ["4", "Create Backup on Server"],
        ["5", "Restore Backup"],
        ["6", "Restore from Downloads"],
        ["7", "Restore in Browser"],
        ["8", "Delete in Browser"],
        ["9", "Exit"],
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
        bc.list_backup()
    elif choice == 2:
        print("Creating backup...")
        bc = Backup()
        bc.make_backup()
    elif choice == 3:
        print("Creating backup and copying to mount...")
        bc = Backup()
        bc.create_and_copy_to_mnt()
    elif choice == 4:
        print("Creating backup on server...")
        bc = Backup()
        bc.make_backup_in_chrome()
    elif choice == 5:
        print("Restoring backup...")
        bc = Backup()
        bc.restore_backup()
    elif choice == 6:
        print("Restoring from downloads...")
        bc = Backup()
        bc.restore_from_downloads()
    elif choice == 7:
        print("Restoring in browser...")
        bc = Backup()
        bc.restore_backup_in_chrome()
    elif choice == 8:
        print("Deleting backup in browser...")
        bc = Backup()
        bc.delete_backup_in_chrome()
    elif choice == 9:
        print("Exiting backup menu...")
        return
