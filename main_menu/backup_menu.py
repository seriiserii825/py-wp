from classes.backup.Backup import Backup
from classes.utils.Menu import Menu
from main_menu.check_for_base_plugins import check_for_base_plugins


def backup_menu():
    check_for_base_plugins()

    menu_header = ["Index", "Action"]
    menu_colors = {
        0: "green",
        1: "yellow",
        2: "yellow",
        3: "yellow",
        4: "blue",
        5: "blue",
        6: "blue",
        7: "red",
        8: "red",
    }
    menu_items = [
        ["0", "List Backups"],
        ["1", "Create Backup"],
        ["2", "Create and Copy to Mount"],
        ["3", "Create Backup on Server"],
        ["4", "Restore Backup"],
        ["5", "Restore from Downloads"],
        ["6", "Restore in Browser"],
        ["7", "Delete in Browser"],
        ["8", "Exit"],
    ]

    Menu.display(
        title="Backup Menu",
        columns=menu_header,
        rows=menu_items,
        row_styles=menu_colors,
    )

    choice = Menu.choose_option()
    if choice == 0:
        print("Listing backups...")
        bc = Backup()
        bc.list_backup()
    elif choice == 1:
        print("Creating backup...")
        bc = Backup()
        bc.make_backup()
    elif choice == 2:
        print("Creating backup and copying to mount...")
        bc = Backup()
        bc.create_and_copy_to_mnt()
    elif choice == 3:
        print("Creating backup on server...")
        bc = Backup()
        bc.make_backup_in_chrome()
    elif choice == 4:
        print("Restoring backup...")
        bc = Backup()
        bc.restore_backup()
    elif choice == 5:
        print("Restoring from downloads...")
        bc = Backup()
        bc.restore_from_downloads()
    elif choice == 6:
        print("Restoring in browser...")
        bc = Backup()
        bc.restore_backup_in_chrome()
    elif choice == 7:
        print("Deleting backup in browser...")
        bc = Backup()
        bc.delete_backup_in_chrome()
    elif choice == 8:
        print("Exiting backup menu...")
        return
