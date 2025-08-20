from pathlib import Path
from classes.files.FileWriter import FileWriter
from classes.files.AbstractFileCreator import AbstractFileCreator
from classes.utils.Command import Command


class SCSSFileCreator(AbstractFileCreator):
    def get_root_dir(self) -> str:
        return "src/scss/blocks"

    def get_extension(self) -> str:
        return "scss"

    def template_to_file(self, file_path: str) -> None:
        file_name = Path(file_path).stem

        # 1. Write SCSS template
        content = f".{file_name} {{\n}}\n"
        FileWriter.write_file(Path(file_path), content)

        template_path = file_path.split("src/scss/")[-1].replace(".scss", "")

        # 3. Generate and insert @use line
        my_scss = Path("src/scss/my.scss")
        import_str = self.use_or_import(str(my_scss))
        import_line = f'{import_str} "{template_path}";\n'

        if my_scss.exists():
            content = my_scss.read_text()
            if import_line not in content:
                my_scss.write_text(content + import_line)
        else:
            my_scss.write_text(import_line)
        Command.run(f"bat '{str(Path(my_scss).resolve())}'")

    def use_or_import(self, file_path: str) -> str:
        # check if first line start with @use or @import
        with open(file_path, 'r') as file:
            first_line = file.readline().strip()
            if first_line.startswith('@use'):
                return '@use'
            elif first_line.startswith('@import'):
                return '@import'
            else:
                return '@import'
