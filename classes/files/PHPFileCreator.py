from classes.files.AbstractFileCreator import AbstractFileCreator
from classes.files.PathManagerEnum import PathManagerEnum
from classes.files.PhpTemplateToFile import PhpTemplateToFile


class PHPFileCreator(AbstractFileCreator):
    def get_root_dir(self) -> str:
        return PathManagerEnum.PHPFILE.value

    def get_extension(self) -> str:
        return "php"

    def template_to_file(self, file_path: str) -> None:
        PhpTemplateToFile.php_to_file(file_path)
