from pathlib import Path
from classes.files.FileWriter import FileWriter
from classes.files.AbstractFileCreator import AbstractFileCreator
from classes.files.PathManagerEnum import PathManagerEnum
from classes.utils.Command import Command


class SCSSFileCreator(AbstractFileCreator):
    def get_root_dir(self) -> str:
        return PathManagerEnum.SCSSFILE.value

    def get_extension(self) -> str:
        return "scss"

    def template_to_file(self, file_path: str) -> None:
        file_name = Path(file_path).stem

        # 1. Write SCSS template
        content = f".{file_name} {{\n}}\n"
        FileWriter.write_file(Path(file_path), content)

        template_path = file_path.split("src/scss/")[-1].replace(".scss", "")

        # 3. Generate and insert @use line
        import_line = f'@use "{template_path}";\n'
        my_scss = Path("src/scss/my.scss")

        if my_scss.exists():
            content = my_scss.read_text()
            if import_line not in content:
                my_scss.write_text(content + import_line)
        else:
            my_scss.write_text(import_line)
        Command.run(f"bat '{str(Path(my_scss).resolve())}'")
