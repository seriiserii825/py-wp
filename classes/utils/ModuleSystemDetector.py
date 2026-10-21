import re
from pathlib import Path


class ModuleSystemDetector:
    MODULES_DIR = Path("modules")
    VITE_CONFIG = Path("vite.config.js")
    SYSTEM_TYPE_FILE = Path(".system-type")
    MODULES = "modules"
    STANDARD = "standard"

    @classmethod
    def load(cls) -> bool | None:
        if not cls.SYSTEM_TYPE_FILE.exists():
            return None
        value = cls.SYSTEM_TYPE_FILE.read_text().strip()
        if value == cls.MODULES:
            return True
        if value == cls.STANDARD:
            return False
        return None

    @classmethod
    def save(cls, is_modules: bool) -> None:
        value = cls.MODULES if is_modules else cls.STANDARD
        cls.SYSTEM_TYPE_FILE.write_text(value + "\n")

    @classmethod
    def detect(cls) -> bool:
        return cls._has_modules_dir() and cls._has_alias_in_vite()

    @classmethod
    def _has_modules_dir(cls) -> bool:
        return cls.MODULES_DIR.is_dir()

    @classmethod
    def _has_alias_in_vite(cls) -> bool:
        if not cls.VITE_CONFIG.exists():
            return False
        for line in cls.VITE_CONFIG.read_text().splitlines():
            stripped = line.strip()
            if stripped.startswith("//"):
                continue
            if re.search(r"""['"]@['"]\s*:\s*path\.resolve""", stripped):
                return True
        return False
