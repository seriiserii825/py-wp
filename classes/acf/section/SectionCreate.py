from pathlib import Path

from classes.utils.InputValidator import InputValidator
from classes.utils.Print import Print


class SectionCreate:
    section_name: str = ""
    file_name: str = ""
    file_path: str = ""

    @classmethod
    def add_name_and_file_path(cls):
        cls.section_name = InputValidator.get_string("Enter section name: ")
        cls.file_name = cls.section_name.replace(" ", "_").lower() + ".json"
        if not Path('acf').exists():
            Path("acf").mkdir(parents=True, exist_ok=True)
        cls.file_path = f"acf/{cls.file_name}"
        if Path(cls.file_path).exists():
            Print.error(f"File {cls.file_path} already exists.")
            cls.add_name_and_file_path()
        else:
            Path(cls.file_path).touch()
            Print.success(f"File {cls.file_path} created successfully.")
