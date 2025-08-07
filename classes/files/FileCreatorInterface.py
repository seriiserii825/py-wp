from abc import ABC, abstractmethod


class FileCreatorInterface(ABC):
    @abstractmethod
    def create_file(self) -> str:
        pass

    @abstractmethod
    def template_to_file(self, file_path: str) -> None:
        pass
