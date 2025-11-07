from pathlib import Path
from classes.files.AbstractFileCreator import AbstractFileCreator
from classes.files.PHPBlockFileCreator import PHPBlockFileCreator
from classes.files.PhpTemplateToFile import PhpTemplateToFile
from classes.utils.Command import Command
from classes.files.SCSSFileCreator import SCSSFileCreator


class PHPBSFileCreator(AbstractFileCreator):
    def get_root_dir(self) -> str:
        return "template-parts"

    def get_extension(self) -> str:
        return "php"

    def template_to_file(self, file_path: str) -> None:
        self._scss(file_path)
        self._block(file_path)

    def _scss(self, file_path: str):
        template_path = PhpTemplateToFile.php_to_file(file_path)

        # Also create SCSS file with same name under `src/scss/blocks/`
        scss_creator = SCSSFileCreator()
        scss_file_path = f"{Path('src/scss/blocks')}/{template_path}.scss"
        scss_creator.template_to_file(str(scss_file_path))

        # Show both files with bat
        Command.run(f"bat '{str(Path(file_path).resolve())}'")
        Command.run(f"bat '{scss_file_path}'")

    def _block(self, file_path: str):
        template_path = PhpTemplateToFile.php_to_file(file_path)
        print(f"template_path: {template_path}")
        exit(1)

        # Also create SCSS file with same name under `src/scss/blocks/`
        block_creator = PHPBlockFileCreator()
        block_file_path = f"{Path('blocks/')}/{template_path}.php"
        block_creator.template_to_file(str(block_file_path))

        # Show both files with bat
        Command.run(f"bat '{str(Path(file_path).resolve())}'")
        Command.run(f"bat '{block_file_path}'")
