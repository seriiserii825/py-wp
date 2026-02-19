import os
from classes.files.FilesHandle import FilesHandle
from classes.selenium.MySelenium import MySelenium
from classes.utils.Command import Command
from classes.utils.WPPaths import WPPaths
from rich import print


class Backup:
    def __init__(self):
        self.backup_dir_abs_path = str(WPPaths.get_backups_path())
        self.theme_dir_path = WPPaths.get_theme_path()
        self.driver = None

    def make_backup(self):
        self.list_backup()
        self._delete_node_modules()
        self._delete_vendor()
        Command.run("wp ai1wm backup")
        self._deleteMore3Backups()
        self.list_backup()
        self._last_backup_to_downloads()

    def _delete_vendor(self):
        if os.path.exists(f"{self.theme_dir_path}/vendor"):
            os.system(f"rm -rf {self.theme_dir_path}/vendor")
            print("[green]vendor deleted successfully.")

    def _delete_node_modules(self):
        if os.path.exists(f"{self.theme_dir_path}/node_modules"):
            os.system(f"rm -rf {self.theme_dir_path}/node_modules")
            print("[green]node_modules deleted successfully.")

    def _deleteMore3Backups(self):
        os.chdir(self.backup_dir_abs_path)
        backup_files = os.listdir()
        backup_files.sort(key=lambda x: os.path.getctime(x), reverse=True)
        backups_array = []
        for file in backup_files:
            if file.endswith(".wpress"):
                backups_array.append(file)
        if len(backups_array) == 0:
            print("[red]No backups found!")
        elif len(backups_array) > 2:
            backup_to_delete = backups_array[2:]
            print("[red]Backups to delete: ")
            for file in backup_to_delete:
                print(file)
            for file in backup_to_delete:
                os.system(f"rm {file}")
        else:
            print("[green]Backups less than 3")

    def make_backup_in_chrome(self):
        ms = MySelenium()
        ms.make_backup_in_chrome()

    def list_backup(self):
        os.system("wp ai1wm list-backups")

    def restore_backup(self):
        self.list_backup()
        fh = FilesHandle()
        selected_backup = fh.choose_file(self.backup_dir_abs_path, ".wpress")
        os.system(f"wp ai1wm restore {selected_backup}")

    def restore_backup_in_chrome(self):
        ms = MySelenium()
        ms.restore_backup_in_chrome()

    def restore_from_downloads(self):
        downloads_dir = os.path.expanduser("~/Downloads")
        fh = FilesHandle()
        fh.list_files(downloads_dir, ".wpress", mtime=True)
        selected_backup = fh.choose_file(downloads_dir, ".wpress")
        print(f"selected_backup: {selected_backup}")
        os.system(f'cp ~/Downloads/{selected_backup} "{self.backup_dir_abs_path}"')
        self.list_backup()
        os.system(f"wp ai1wm restore {selected_backup}")

    def delete_backup_in_chrome(self):
        ms = MySelenium()
        ms.delete_backup_in_chrome()

    def get_last_backup_path(self):
        os.chdir(self.backup_dir_abs_path)
        backup_files = os.listdir()
        backup_files.sort(key=lambda x: os.path.getctime(x), reverse=True)
        if len(backup_files) == 0:
            print("[red]No backups found!")
        else:
            return backup_files[0]

    def _last_backup_to_downloads(self):
        last_backup = self.get_last_backup_path()
        if last_backup:
            backup_path = f"{self.backup_dir_abs_path}/{last_backup}"
            destination = os.path.expanduser("~/Downloads")
            Command.run(f'cp "{backup_path}" {destination}')
            print(f"[green]Last backup copied to ~/Downloads/{last_backup}")
        else:
            print("[red]No backups found to copy.")

    def last_backup_to_mnt(self, mnt_path):
        last_backup = self.get_last_backup_path()
        if last_backup:
            backup_path = f"{self.backup_dir_abs_path}/{last_backup}"
            Command.run(f"cp '{backup_path}' '{mnt_path}'")
        else:
            print("[red]No backups found to copy.")

    def create_and_copy_to_mnt(self):
        directory_exists = os.path.isdir("/mnt/Projects")
        if directory_exists:
            path_to_dir = "/mnt/Projects"
            fh = FilesHandle()
            path_to_selected_dir = fh.create_or_choose_directory(path_to_dir)
            fh.list_dir(path_to_selected_dir)
            path_to_selected_dir = fh.create_or_choose_directory(path_to_selected_dir)
            self.make_backup()
            self.last_backup_to_mnt(path_to_selected_dir)
            last_backup = self.get_last_backup_path()
            print(f"[green]Backup created and copied to /mnt/Projects/{last_backup}")
            self.remove_backups_on_mnt_by_count(path_to_selected_dir)
        else:
            exit("[red]Directory /mnt/Projects not exists!")

    def remove_backups_on_mnt_by_count(self, mnt_path, count=6):
        if os.path.isdir(mnt_path):
            os.chdir(mnt_path)
            backups_array = self._files_to_array()
            if len(backups_array) == 0:
                print("[red]No backups found on mount!")
            elif len(backups_array) > count:
                self._list_files(backups_array)
                backup_to_delete = backups_array[count:]
                print(f"[red]Backups to delete on {mnt_path}: ")
                self._list_files(backup_to_delete)
                agree_to_delete = input(
                    f"[yellow]Do you want to delete these backups on {mnt_path}? (y/n): "
                )
                if agree_to_delete.lower() == "y":
                    for file in backup_to_delete:
                        os.system(f"rm {file}")
                    new_files_on_mnt = self._files_to_array()
                    print(f"[green]Backups deleted. Current backups on {mnt_path}: ")
                    self._list_files(new_files_on_mnt)
                else:
                    print("[green]Backups not deleted.")
            else:
                print(f"[green]Backups on {mnt_path} less than or equal to {count}")
        else:
            print(f"[red]Directory {mnt_path} does not exist!")

    def _list_files(self, files):
        for file in files:
            print(file)

    def _files_to_array(self):
        backup_files = os.listdir()
        backup_files.sort(key=lambda x: os.path.getctime(x), reverse=True)
        backups_array = []
        for file in backup_files:
            if file.endswith(".wpress"):
                backups_array.append(file)
        return backups_array
