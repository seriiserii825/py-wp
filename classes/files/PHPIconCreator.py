import pyperclip
from pathlib import Path
from classes.files.FileWriter import FileWriter
from classes.files.AbstractFileCreator import AbstractFileCreator
from classes.utils.Command import Command
from classes.utils.Notification import Notification
from classes.utils.Print import Print
from classes.utils.InputValidator import InputValidator
from classes.files.FilesHandle import FilesHandle


class PHPIconCreator(AbstractFileCreator):
    def get_root_dir(self) -> str:
        try:
            self._get_svg_from_clipboard()
        except ValueError as e:
            Print.error(f"Error: {e}")
            exit(1)
        return "template-parts/icons"

    def get_extension(self) -> str:
        return "php"

    def _file_path(self, path_to_dir) -> str:
        file_name = InputValidator.get_string(
            "Enter icon name, icon- will be added: ")
        file_name = f"icon-{file_name}"
        file_name = self._remove_extension(file_name)
        file_name = self._clear_whitespaces(file_name)
        file_name = self._add_extension(file_name, self.get_extension())
        return str(Path(path_to_dir) / file_name)

    def template_to_file(self, file_path: str) -> None:
        try:
            svg = self._get_svg_from_clipboard()
        except ValueError as e:
            Print.error(f"Error: {e}")
            return
        html = svg

        FileWriter.write_file(Path(file_path), html)
        template_path = file_path
        Command.run(f"bat '{str(Path(template_path).resolve())}'")
        self._copy_template_part_to_clipboard(template_part=template_path)

    def _get_svg_from_clipboard(self) -> str:
        svg = pyperclip.paste()
        if not svg.startswith("<svg"):
            raise ValueError("Clipboard does not contain valid SVG data.")
        return svg

    def _copy_template_part_to_clipboard(self, template_part: str) -> None:
        template_part = template_part.replace(".php", "")
        text = f"<?php get_template_part('{template_part}'); ?>"
        pyperclip.copy(text)
        nt = Notification(title=text, message="Template part copied to clipboard")
        nt.notify()
