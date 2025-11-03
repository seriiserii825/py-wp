import os
from typing import List

from classes.exception.NewSectionException import NewSectionException
from classes.utils.Select import Select


class SelectSection:
    @staticmethod
    def get_sections_files() -> List[str]:
        if not os.path.exists("acf"):
            raise NewSectionException("The 'acf' directory does not exist.")
        files = [f for f in os.listdir("acf") if f.endswith(".json")]
        return files

    @classmethod
    def select_section(cls) -> str:
        file_name = Select.select_with_fzf(cls.get_sections_files())
        return f"acf/{file_name[0]}"
