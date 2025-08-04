import os

from pyfzf.pyfzf import FzfPrompt
from rich import print
from simple_term_menu import TerminalMenu

from classes.utils.Select import Select


class FilesHandle:
    def __init__(self, basepath: str = ""):
        self.basepath = basepath if basepath != "" else "."
        print(f"self.basepath: {self.basepath}")

    def listFiles(self, path_to_list=""):
        if path_to_list:
            self.basepath = path_to_list
        print(f"[green]Listing files in ================ {self.basepath}")
        for entry in os.listdir(self.basepath):
            if os.path.isfile(os.path.join(self.basepath, entry)):
                print(entry)

    def listDir(self, path_to_list=""):
        if path_to_list:
            self.basepath = path_to_list
        print(f"[blue]Listing directories in ================ {self.basepath}")
        with os.scandir(self.basepath) as entries:
            for entry in entries:
                if entry.is_dir():
                    print(entry.name)

    def createOrChooseDirectory(self, path_to_dir=""):
        if path_to_dir:
            self.basepath = path_to_dir
        else:
            self.basepath = os.getcwd()
        self.listDir(self.basepath)
        select_or_create = Select.select_one(["Select", "Create"])
        if select_or_create == "Create":
            dir_name = input("Enter directory name:")
            if dir_name == "":
                print("Directory name is required")
                exit()
            else:
                os.makedirs(self.basepath + "/" + dir_name)
                print("Directory created")
                return dir_name
        else:
            selected_dir = self.chooseDir()
            return selected_dir

    def chooseDir(self):
        choosed_dir = []
        with os.scandir(self.basepath) as entries:
            for entry in entries:
                if entry.is_dir():
                    choosed_dir.append(entry.name)
        choosed_dir.sort()
        selected_dir = Select.select_with_fzf(choosed_dir)
        return selected_dir

    def listFilesWithPrefix(self, prefix):
        print(f"Listing directories in ================ {self.basepath}")
        for entry in os.listdir(self.basepath):
            if os.path.isfile(os.path.join(self.basepath, entry)):
                for item in prefix:
                    if entry.startswith(item):
                        print(entry)
        print(f"Listing directories in ================ {self.basepath}")

    def selectWithFzf(self, items):
        fzf = FzfPrompt()
        selected_item = fzf.prompt(items)
        return selected_item[0]

    def chooseFile(self, path_to_dir, extension=None):
        choosed_files = []
        for entry in os.listdir(path_to_dir):
            if os.path.isfile(os.path.join(path_to_dir, entry)):
                if extension:
                    if entry.endswith(extension):
                        choosed_files.append(entry)
                else:
                    choosed_files.append(entry)
        if len(choosed_files) == 0:
            exit("[red]No files found")
        else:
            return Select.select_one(choosed_files)

    def appendToFile(self, file_path, text):
        with open(file_path, "a") as f:
            f.write(text)
        os.system(f"bat {file_path}")

    def selectMultiple(self, options):
        terminal_menu = TerminalMenu(
            options,
            multi_select=True,
            show_multi_select_hint=True,
            show_search_hint=True,
            preview_command="bat --color=always {}",
            preview_size=0.75,
        )
        terminal_menu.show()
        return terminal_menu.chosen_menu_entries
