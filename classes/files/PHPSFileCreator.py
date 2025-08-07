from pathlib import Path
from classes.files.AbstractFileCreator import AbstractFileCreator
from classes.files.PathManagerEnum import PathManagerEnum
from classes.files.PhpTemplateToFile import PhpTemplateToFile
from classes.utils.Command import Command
from classes.files.SCSSFileCreator import SCSSFileCreator


class PHPSFileCreator(AbstractFileCreator):
    def get_root_dir(self) -> str:
        return PathManagerEnum.PHPFILE.value

    def get_extension(self) -> str:
        return "php"

    def template_to_file(self, file_path: str) -> None:
        template_path = PhpTemplateToFile.php_to_file(file_path)

        # Also create SCSS file with same name under `src/scss/blocks/`
        scss_creator = SCSSFileCreator()
        scss_file_path = f"{Path('src/scss/blocks')}/{template_path}"
        scss_creator.template_to_file(str(scss_file_path))

        # Show both files with bat
        Command.run(f"bat '{str(Path(file_path).resolve())}'")
        Command.run(f"bat '{scss_file_path}'")
