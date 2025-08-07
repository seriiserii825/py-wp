from pathlib import Path
from classes.files.AbstractFileCreator import AbstractFileCreator
from classes.files.FileWriter import FileWriter
from classes.utils.Command import Command
from classes.files.SCSSFileCreator import SCSSFileCreator


class PHPSFileCreator(AbstractFileCreator):
    def get_root_dir(self) -> str:
        return "template-parts"

    def get_extension(self) -> str:
        return "php"

    def template_to_file(self, file_path: str) -> None:
        file_name = Path(file_path).stem
        html = f'<div class="{file_name}">\n</div>\n'
        FileWriter.write_file(Path(file_path), html)

        # Add to front-page.php
        template_path = file_path.split("template-parts/")[-1].replace(".php", "")
        print(f"template_path: {template_path}")
        front_page = Path("front-page.php")

        if front_page.exists():
            include = f'<?php get_template_part("template-parts/{template_path}"); ?>\n'
            content = front_page.read_text()
            if include not in content:
                lines = content.splitlines(keepends=True)
                for i, line in enumerate(lines):
                    if "get_footer" in line:
                        lines.insert(i, include)
                        break
                else:
                    lines.append(include)
                front_page.write_text("".join(lines))
        else:
            print("front-page.php does not exist. Skipping include.")

        # Also create SCSS file with same name under `src/scss/blocks/`
        scss_creator = SCSSFileCreator()
        scss_file_path = f"{Path('src/scss/blocks')}/{template_path}"
        scss_creator.template_to_file(str(scss_file_path))

        # Show both files with bat
        Command.run(f"bat '{str(Path(file_path).resolve())}'")
        Command.run(f"bat '{scss_file_path}'")
