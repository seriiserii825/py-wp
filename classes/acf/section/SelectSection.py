import os
from typing import List

from rich.markup import escape

from classes.exception.NewSectionException import NewSectionException
from classes.utils.ColorMenu import ColorMenu


class SelectSection:
    @staticmethod
    def get_sections_files() -> List[str]:
        if not os.path.exists("acf"):
            raise NewSectionException("The 'acf' directory does not exist.")
        files = [f for f in os.listdir("acf") if f.endswith(".json")]
        return files

    @staticmethod
    def choose(files: List[str], title: str | None = None) -> str | None:
        """Colored fzf menu of section files; Back / Esc → None."""
        index = ColorMenu.select(
            [f"[green]{escape(f)}" for f in files],
            title=title,
            exit_label="[red]Back",
        )
        return None if index == len(files) else files[index]

    @classmethod
    def select_section(cls) -> str | None:
        file_name = cls.choose(cls.get_sections_files(), "Select section")
        return None if file_name is None else f"acf/{file_name}"
