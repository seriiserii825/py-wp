# classes/factory/FileCreatorFactory.py
from classes.files.FileCreatorInterface import FileCreatorInterface
from classes.files.PHPFileCreator import PHPFileCreator
from classes.files.PHPIconCreator import PHPIconCreator
from classes.files.PHPPageCreator import PHPPageCreator
from classes.files.PHPSFileCreator import PHPSFileCreator
from classes.files.SCSSFileCreator import SCSSFileCreator
from enum_folder.FileTypeEnum import FileTypeEnum


class FileCreatorFactory:
    @staticmethod
    def get_creator(file_type_enum: FileTypeEnum) -> FileCreatorInterface:
        match file_type_enum:
            case FileTypeEnum.PHP:
                return PHPFileCreator()
            case FileTypeEnum.PHPS:
                return PHPSFileCreator()
            case FileTypeEnum.SCSS:
                return SCSSFileCreator()
            case FileTypeEnum.PHPP:
                return PHPPageCreator()
            case FileTypeEnum.PHPI:
                return PHPIconCreator()
            # Add more cases
            case _:
                raise ValueError(f"No creator defined for {file_type_enum}")
