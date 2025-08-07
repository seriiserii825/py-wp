from pathlib import Path
from classes.files.FileWriter import FileWriter
from classes.files.AbstractFileCreator import AbstractFileCreator
from classes.files.FilesHandle import FilesHandle
from classes.utils.Command import Command
from classes.utils.InputValidator import InputValidator


class PHPPageCreator(AbstractFileCreator):
    def get_root_dir(self) -> str:
        return "."

    def get_extension(self) -> str:
        return "php"

    def _file_path(self, path_to_dir) -> str:
        FilesHandle().list_files(path_to_dir, "php")
        file_name = InputValidator.get_string("Enter file name without extension: ")
        file_name = self._remove_extension(file_name)
        file_name = self._clear_whitespaces(file_name)
        file_name = self._add_extension(file_name, self.get_extension())
        return str(Path(path_to_dir) / file_name)

    def template_to_file(self, file_path: str) -> None:
        html = "<?php get_header();?>\n<?php get_footer()?>\n"
        FileWriter.write_file(Path(file_path), html)

        template_path = file_path.split("/")[-1]

        Command.run(f"bat '{str(Path(template_path).resolve())}'")
