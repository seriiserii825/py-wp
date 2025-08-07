from pathlib import Path
from classes.files.FileWriter import FileWriter
from classes.files.AbstractFileCreator import AbstractFileCreator
from classes.utils.Command import Command


class PHPPageCreator(AbstractFileCreator):
    def get_root_dir(self) -> str:
        return "."

    def get_extension(self) -> str:
        return "php"

    def template_to_file(self, file_path: str) -> None:
        html = "<?php get_header();?>\n<?php get_footer()?>\n"
        FileWriter.write_file(Path(file_path), html)

        template_path = file_path.split("/")[-1]

        Command.run(f"bat '{str(Path(template_path).resolve())}'")
