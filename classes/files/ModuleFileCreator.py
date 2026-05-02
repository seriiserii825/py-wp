from pathlib import Path

from classes.files.AbstractFileCreator import AbstractFileCreator
from classes.files.FileWriter import FileWriter
from classes.utils.Command import Command
from classes.utils.InputValidator import InputValidator
from classes.utils.Select import Select


class ModuleFileCreator(AbstractFileCreator):
    _EXTENSIONS = {"php": "php", "scss": "scss", "js": "ts"}

    def __init__(self, module_path: str, file_type: str):
        self._module_path = module_path
        self._file_type = file_type

    def get_root_dir(self) -> str:
        return self._module_path

    def get_extension(self) -> str:
        return self._EXTENSIONS[self._file_type]

    def template_to_file(self, file_path: str) -> None:
        match self._file_type:
            case "php":
                self._write_php(file_path)
            case "scss":
                self._write_scss(file_path)
            case "js":
                self._write_js(file_path)

        Command.run(f"bat '{Path(file_path).resolve()}'")

    # --- templates ---

    def _write_php(self, file_path: str) -> None:
        name = Path(file_path).stem
        content = f"<?php\nif (!defined('ABSPATH')) exit;\n?>\n\n<div class=\"{name}\">\n</div>\n"
        FileWriter.write_file(Path(file_path), content)
        self._offer_get_template_part(file_path)

    def _write_scss(self, file_path: str) -> None:
        name = Path(file_path).stem
        content = f".{name} {{\n}}\n"
        FileWriter.write_file(Path(file_path), content)
        self._append_scss_import(file_path)

    def _write_js(self, file_path: str) -> None:
        name = Path(file_path).stem
        content = f"export default function {name}() {{\n}}\n"
        FileWriter.write_file(Path(file_path), content)

    # --- side effects ---

    def _append_scss_import(self, file_path: str) -> None:
        my_scss = Path("src/scss/my.scss")
        if not my_scss.exists():
            return

        module_name = Path(self._module_path).name
        file_name = Path(file_path).stem
        import_line = f"@use '@/modules/{module_name}/{file_name}';\n"

        content = my_scss.read_text()
        if import_line not in content:
            my_scss.write_text(content + import_line)
        Command.run(f"bat '{my_scss.resolve()}'")

    def _offer_get_template_part(self, file_path: str) -> None:
        if not InputValidator.get_bool("Include in a PHP file? (y/n): "):
            return

        php_files = sorted(str(f) for f in Path(".").glob("*.php"))
        if not php_files:
            return

        selected = Select.select_with_fzf(php_files)
        if not selected:
            return

        module_name = Path(self._module_path).name
        file_name = Path(file_path).stem
        snippet = f'<?php get_template_part(\'modules/{module_name}/{file_name}\'); ?>\n'

        target = Path(selected[0])
        content = target.read_text()
        if snippet in content:
            return

        lines = content.splitlines(keepends=True)
        for i, line in enumerate(lines):
            if "get_footer" in line:
                lines.insert(i, snippet)
                break
        else:
            lines.append(snippet)

        target.write_text("".join(lines))
        Command.run(f"bat '{target.resolve()}'")
