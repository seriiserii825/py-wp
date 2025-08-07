from pathlib import Path
from classes.files.FileCreatorInterface import FileCreatorInterface
from classes.files.FilesHandle import FilesHandle
from classes.utils.InputValidator import InputValidator


class PHPFileCreator(FileCreatorInterface):
    def create_file(self) -> str:
        root_dir = "template-parts"
        dir_path = self._get_dir_path(root_dir)
        file_path = self._file_path(dir_path)
        self._create_file(file_path)
        return file_path

    def _get_dir_path(self, root_dir) -> str:
        base_path = Path(root_dir).resolve()
        current_path = str(base_path)

        while True:
            selected_path = FilesHandle().create_or_choose_directory(str(current_path))
            current_path = selected_path

            print(f"Selected folder: {current_path}")
            choice = input("Go deeper into subfolder? (y/n): ").strip().lower()

            if choice != "y":
                break

        return str(Path(current_path).resolve())

    def _file_path(self, path_to_dir) -> str:
        FilesHandle().list_files(path_to_dir)
        file_name = InputValidator.get_string("Enter file name without extension: ")
        file_name = self._remove_extension(file_name)
        file_name = file_name.strip()
        file_name = self._clear_whitespaces(file_name)
        file_name = self._add_extension(file_name, "php")
        return str(Path(f"{path_to_dir}/{file_name}").resolve())

    def _remove_extension(self, file_name: str) -> str:
        if "." in file_name:
            return file_name.split(".")[0]
        return file_name

    def _clear_whitespaces(self, file_name: str) -> str:
        return file_name.strip().replace(" ", "-").lower()

    def _add_extension(self, file_name: str, extension: str) -> str:
        if not file_name.endswith(f".{extension}"):
            return f"{file_name}.{extension}"
        return file_name

    def _create_file(self, file_path: str) -> None:
        file_abs_path = Path(file_path).resolve()
        if file_abs_path.exists():
            overwrite = input("File already exists. Overwrite? (y/n): ")
            if overwrite.strip().lower() != "y":
                print("Aborted.")
                return
        if not file_abs_path.exists():
            file_abs_path.touch()
        file_abs_path.parent.mkdir(parents=True, exist_ok=True)
        # html = f'<div class="{filename}">\n</div>\n'
        # FileWriter.write_file(php_path, html)

        # front_page = Path("front-page.php")
        # if front_page.exists():
        #     include = (
        #         f"<?php"
        #         f' get_template_part("{php_path.relative_to("template-parts")}"); ?>\n'
        #     )
        #     if include not in front_page.read_text():
        #         with front_page.open("a") as f:
        #             f.write(include)
