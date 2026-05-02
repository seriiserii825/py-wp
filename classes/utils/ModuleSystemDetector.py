import re
from pathlib import Path


class ModuleSystemDetector:
    MODULES_DIR = Path("modules")
    VITE_CONFIG = Path("vite.config.js")

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
