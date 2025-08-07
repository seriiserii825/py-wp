from enum import Enum


class FileTypeEnum(Enum):
    PHP = ("php", True)
    PHPS = ("phps", True)
    PHPP = ("phpp", False)
    PHPI = ("phpi", True)
    SCSS = ("scss", True)
    JS = ("js", True)

    def __init__(self, label: str, use_dir: bool):
        self.label = label
        self.use_dir = use_dir
