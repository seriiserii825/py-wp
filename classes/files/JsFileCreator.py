from pathlib import Path
from classes.files.FileWriter import FileWriter
from classes.files.AbstractFileCreator import AbstractFileCreator
from classes.utils.Command import Command


class JsFileCreator(AbstractFileCreator):
    def get_root_dir(self) -> str:
        return "src/js/modules"

    def get_extension(self) -> str:
        return "ts"

    def template_to_file(self, file_path: str) -> None:
        file_name = Path(file_path).stem

        content = f"export default function {file_name}() {{\n}}\n"
        FileWriter.write_file(Path(file_path), content)

        Command.run(f"bat '{str(Path(file_path).resolve())}'")
