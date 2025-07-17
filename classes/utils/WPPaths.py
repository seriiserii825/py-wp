import inspect
import json
from enum import Enum
from pathlib import Path
from typing import Dict, Optional


class PathKey(str, Enum):
    BASE = "base_dir"
    WP_CONTENT = "wp_content_dir"
    UPLOADS = "uploads_dir"
    PLUGINS = "plugins_dir"
    THEME = "theme_dir"


class WPPaths:
    _paths: Dict[str, str] = {}
    _paths_file: Optional[Path] = None

    @classmethod
    def initialize(cls, base_dir: Optional[Path] = None):
        """Вычисляет пути и сохраняет в .paths.json"""
        cls._ensure_paths_file()
        assert cls._paths_file is not None

        if base_dir is None:
            base_dir = Path.cwd()

        wp_content = base_dir.parent.parent  # themes/lm-omp → wp-content

        cls._paths = {
            PathKey.BASE.value: str(base_dir.resolve()),
            PathKey.WP_CONTENT.value: str(wp_content.resolve()),
            PathKey.UPLOADS.value: str((wp_content / "uploads").resolve()),
            PathKey.PLUGINS.value: str((wp_content / "plugins").resolve()),
            PathKey.THEME.value: str(base_dir.resolve()),
        }

        with open(cls._paths_file, "w") as f:
            json.dump(cls._paths, f, indent=2)

    @classmethod
    def _get_script_dir(cls) -> Path:
        # Путь к текущему файлу, где находится этот класс
        return Path(inspect.getfile(cls)).resolve().parent

    @classmethod
    def _ensure_paths_file(cls):
        if cls._paths_file is None:
            cls._paths_file = cls._get_script_dir() / ".paths.json"

    @classmethod
    def load(cls):
        """Загружает пути из .paths.json"""
        cls._ensure_paths_file()
        assert cls._paths_file is not None

        if not cls._paths:
            if not cls._paths_file.exists():
                raise FileNotFoundError(
                    f"{cls._paths_file} not found. Run initialize() first."
                )
            with open(cls._paths_file) as f:
                cls._paths = json.load(f)

    @classmethod
    def get(cls, key: PathKey) -> Path:
        """Получить путь по ключу"""
        cls.load()
        return Path(cls._paths[key.value])

    @classmethod
    def all(cls) -> Dict[PathKey, Path]:
        """Получить все пути"""
        cls.load()
        return {
            PathKey(k): Path(v)
            for k, v in cls._paths.items()
            if k in PathKey._value2member_map_
        }
