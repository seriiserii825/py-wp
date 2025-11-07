from pathlib import Path

from classes.files.FileWriter import FileWriter
from classes.utils.Command import Command
from classes.utils.InputValidator import InputValidator
from classes.utils.Select import Select
from classes.utils.WPPaths import WPPaths


class PhpTemplateToFile:
    @staticmethod
    def php_to_file(file_path: str) -> str:
        file_name = Path(file_path).stem
        html = f'<?php \n\n ?>\n<div class="{file_name}">\n</div>\n'
        FileWriter.write_file(Path(file_path), html)

        choice = InputValidator.get_bool(
            'Do you want to include this template in another PHP file? (y/n): ')
        if not choice:
            return PhpTemplateToFile._return_path(file_path)

        template_path = file_path.split(
            "template-parts/")[-1].replace(".php", "")

        listed_files = [str(file_name)
                        for file_name in Path(".").glob("*.php")]
        selected_file = Select.select_one(listed_files)
        file_to_include = Path(selected_file)
        include = f'<?php get_template_part("template-parts/{template_path}"); ?>\n'
        content = file_to_include.read_text()
        if include not in content:
            lines = content.splitlines(keepends=True)
            for i, line in enumerate(lines):
                if "get_footer" in line:
                    lines.insert(i, include)
                    break
            else:
                lines.append(include)
            file_to_include.write_text("".join(lines))
        Command.run(f"bat '{str(Path(file_to_include).resolve())}'")
        return PhpTemplateToFile._return_path(file_path)

    @staticmethod
    def _return_path(file_path: str) -> str:
        theme_path = WPPaths.get_theme_path()
        them_with_template_parts = f"{theme_path}/template-parts/"
        result = file_path.split(
            them_with_template_parts)[-1].replace(".php", "")
        return result
