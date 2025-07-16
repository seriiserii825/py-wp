import os
from pathlib import Path
import sys


class PathHelper:
    def __init__(self):
        # Путь до точки входа (где был вызван основной скрипт)
        self.entry_point = Path(sys.argv[0]).resolve()

        # Папка, где находится исполняемый скрипт (main.py)
        self.entry_dir = self.entry_point.parent

        # Рабочая директория, откуда был вызван скрипт
        self.cwd = Path(os.getcwd())

    @property
    def get_entry_point(self) -> Path:
        return self.entry_point

    @property
    def get_entry_dir(self) -> Path:
        return self.entry_dir

    @property
    def get_cwd(self) -> Path:
        return Path.cwd()
