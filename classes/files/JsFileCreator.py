from pathlib import Path
from classes.files.FileWriter import FileWriter
from classes.files.AbstractFileCreator import AbstractFileCreator
from classes.utils.Command import Command
from classes.utils.InputValidator import InputValidator


class JsFileCreator(AbstractFileCreator):
    def get_root_dir(self) -> str:
        return "src/js/modules"

    def get_extension(self) -> str:
        return "ts"

    def _transform_file_name(self, file_name: str) -> str:
        if InputValidator.get_bool("Is this an animation module? (y/n): "):
            return f"{self._to_camel_case(file_name)}Animation"
        return file_name

    @staticmethod
    def _to_camel_case(name: str) -> str:
        parts = name.split("-")
        return parts[0] + "".join(
            word[0].upper() + word[1:] if word else "" for word in parts[1:]
        )

    def template_to_file(self, file_path: str) -> None:
        file_name = Path(file_path).stem

        content = f"export default function {file_name}() {{\n}}\n"
        FileWriter.write_file(Path(file_path), content)

        Command.run(f"bat '{str(Path(file_path).resolve())}'")
