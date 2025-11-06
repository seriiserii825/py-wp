from enum import Enum


class FileTypeEnum(Enum):
    PHP = ("php", True)
    PHPBlock = ("phpb", False)
    PHPS = ("phps", True)
    PHPP = ("phpp", False)
    PHPI = ("phpi", False)
    SCSS = ("scss", True)
    JS = ("js", True)
    NONE = ("none", False)

    def __init__(self, label: str, use_dir: bool):
        self.label = label
        self.use_dir = use_dir
