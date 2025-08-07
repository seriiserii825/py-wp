from abc import ABC, abstractmethod


class FileCreatorInterface(ABC):
    @abstractmethod
    def create_file(self) -> str:
        pass
