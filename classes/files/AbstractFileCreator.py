from abc import ABC, abstractmethod
from pathlib import Path
from classes.files.FileCreatorInterface import FileCreatorInterface
from classes.files.FilesHandle import FilesHandle
from classes.utils.InputValidator import InputValidator


class AbstractFileCreator(FileCreatorInterface, ABC):
    def create_file(self, use_dir=True) -> str:
        if use_dir:
            dir_path = self._get_dir_path()
        else:
            dir_path = self.get_root_dir()
        file_path = self._file_path(dir_path)
        self._create_file(file_path)
        return file_path

    def _get_dir_path(self) -> str:
        base_path = Path(self.get_root_dir()).resolve()
        current_path = str(base_path)

        while True:
            selected_path = FilesHandle().create_or_choose_directory(current_path)
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
        file_name = self._clear_whitespaces(file_name)
        file_name = self._add_extension(file_name, self.get_extension())
        return str(Path(path_to_dir) / file_name)

    def _create_file(self, file_path: str) -> None:
        file_abs_path = Path(file_path).resolve()
        if file_abs_path.exists():
            overwrite = input("File already exists. Overwrite? (y/n): ")
            if overwrite.strip().lower() != "y":
                print("Aborted.")
                exit(0)
        file_abs_path.parent.mkdir(parents=True, exist_ok=True)
        file_abs_path.touch(exist_ok=True)

    def _remove_extension(self, file_name: str) -> str:
        return file_name.split(".")[0] if "." in file_name else file_name

    def _clear_whitespaces(self, file_name: str) -> str:
        return file_name.strip().replace(" ", "-")

    def _add_extension(self, file_name: str, extension: str) -> str:
        return (
            f"{file_name}.{extension}"
            if not file_name.endswith(f".{extension}")
            else file_name
        )

    @abstractmethod
    def get_root_dir(self) -> str:
        pass

    @abstractmethod
    def get_extension(self) -> str:
        pass

    @abstractmethod
    def template_to_file(self, file_path: str) -> None:
        pass
