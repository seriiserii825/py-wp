import pyperclip
from pathlib import Path
from classes.files.FileWriter import FileWriter
from classes.files.AbstractFileCreator import AbstractFileCreator
from py_libs.Command import Command
from py_libs.Notification import Notification
from py_libs.Print import Print
from py_libs.InputValidator import InputValidator
from py_libs.FilesHandle import FilesHandle


class PHPIconCreator(AbstractFileCreator):
    def __init__(self) -> None:
        self._multiple = False

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
        self._multiple = not InputValidator.confirm("Create one icon?")
        FilesHandle().list_files(path_to_dir, file_extension=".php")
        file_name = InputValidator.get_string(
            "Enter icon name, icon- will be added: ")
        return self._build_icon_path(path_to_dir, file_name)

    def _build_icon_path(self, path_to_dir: str, file_name: str) -> str:
        file_name = f"icon-{file_name}"
        file_name = self._remove_extension(file_name)
        file_name = self._clear_whitespaces(file_name)
        file_name = self._add_extension(file_name, self.get_extension())
        return str(Path(path_to_dir) / file_name)

    def template_to_file(self, file_path: str) -> None:
        self._write_icon(file_path)
        if not self._multiple:
            return

        dir_path = str(Path(file_path).parent)
        while True:
            FilesHandle().list_files(dir_path, file_extension=".php")
            file_name = InputValidator.get_string(
                "Copy next SVG, then enter icon name (or 'exit'): ")
            if file_name.lower() == "exit":
                exit(0)
            next_path = self._build_icon_path(dir_path, file_name)
            self._create_file(next_path)
            self._write_icon(next_path)

    def _write_icon(self, file_path: str) -> None:
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
