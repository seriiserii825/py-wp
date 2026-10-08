from classes.backup.Backup import Backup
from main_menu.ask_open_browser import ask_and_run_browser_flow
from main_menu.check_for_base_plugins import check_for_base_plugins
from main_menu.table_menu import table_menu


def backup_menu():
    check_for_base_plugins()

    options = [
        "List Backups",
        "Create Backup",
        "Create and Copy to Mount",
        "Create Backup on Server",
        "Restore Backup",
        "Restore from Downloads",
        "Restore in Browser",
        "Delete in Browser",
        "Download Last Backup from Server",
    ]

    choice = table_menu("Backups", options)
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
        ask_and_run_browser_flow(bc.make_backup_in_chrome)
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
        ask_and_run_browser_flow(bc.restore_backup_in_chrome)
        backup_menu()
    elif choice == 7:
        print("Deleting backup in browser...")
        bc = Backup()
        ask_and_run_browser_flow(bc.delete_backup_in_chrome)
        backup_menu()
    elif choice == 8:
        print("Downloading last backup from server...")
        bc = Backup()
        ask_and_run_browser_flow(bc.download_last_backup_from_server)
        backup_menu()
    # Back → return to the main menu
