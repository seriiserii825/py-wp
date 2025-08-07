from dataclasses import dataclass


@dataclass
class FileConfig:
    filename: str
    folder: str
    generate_php: bool
    generate_scss: bool
    scss_autoinject: bool
