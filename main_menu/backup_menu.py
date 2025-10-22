from classes.backup.Backup import Backup
from classes.utils.Menu import Menu
from main_menu.check_for_base_plugins import check_for_base_plugins


def backup_menu():
    check_for_base_plugins()

    menu_items = [
        "0).List Backups",
        "1).Create Backup",
        "2).Create and Copy to Mount",
        "3).Create Backup on Server",
        "4).Restore Backup",
        "5).Restore from Downloads",
        "6).Restore in Browser",
        "7).Delete in Browser",
        "8).Exit",
    ]

    choice = Menu.select_fzf(menu_items)
    if choice == 0:
        print("Listing backups...")
        bc = Backup()
        bc.list_backup()
        backup_menu()
    elif choice == 1:
        print("Creating backup...")
        bc = Backup()
        bc.make_backup()
        backup_menu()
    elif choice == 2:
        print("Creating backup and copying to mount...")
        bc = Backup()
        bc.create_and_copy_to_mnt()
    elif choice == 3:
        print("Creating backup on server...")
        bc = Backup()
        bc.make_backup_in_chrome()
        backup_menu()
    elif choice == 4:
        print("Restoring backup...")
        bc = Backup()
        bc.restore_backup()
        backup_menu()
    elif choice == 5:
        print("Restoring from downloads...")
        bc = Backup()
        bc.restore_from_downloads()
        backup_menu()
    elif choice == 6:
        print("Restoring in browser...")
        bc = Backup()
        bc.restore_backup_in_chrome()
        backup_menu()
    elif choice == 7:
        print("Deleting backup in browser...")
        bc = Backup()
        bc.delete_backup_in_chrome()
        backup_menu()
    elif choice == 8:
        print("Exiting backup menu...")
        return
