import pyperclip
from pathlib import Path
from classes.files.PHPIconCreator import PHPIconCreator
from py_libs.Notification import Notification
from py_libs.Print import Print


class SVGIconCreator(PHPIconCreator):
    def get_root_dir(self) -> str:
        try:
            self._get_svg_from_clipboard()
        except ValueError as e:
            Print.error(f"Error: {e}")
            exit(1)
        root_dir = "assets/i/svg-icons"
        Path(root_dir).mkdir(parents=True, exist_ok=True)
        return root_dir

    def get_extension(self) -> str:
        return "svg"

    def _name_prefix(self) -> str:
        return ""

    def _after_write(self, file_path: str) -> None:
        text = f"<?php bsIcon('{Path(file_path).stem}') ?>"
        pyperclip.copy(text)
        Notification(title=text, message="Copied to clipboard").notify()
