import pyperclip
from pathlib import Path
from classes.files.FileWriter import FileWriter
from classes.files.AbstractFileCreator import AbstractFileCreator
from classes.utils.Command import Command
from classes.utils.Notification import Notification
from classes.utils.Print import Print


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
