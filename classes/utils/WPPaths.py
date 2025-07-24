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
    SCRIPT_DIR = "script_dir"


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
            PathKey.SCRIPT_DIR.value: str(cls.get_script_dir_path()),
        }

        with open(cls._paths_file, "w") as f:
            json.dump(cls._paths, f, indent=2)

    @classmethod
    def _get_script_dir(cls) -> Path:
        """Получает директорию скрипта, где находится .paths.json"""
        script_path = Path(__file__).resolve()
        return script_path.parent

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
    def get_plugin_path(cls) -> Path:
        cls.load()
        return cls.get(PathKey.PLUGINS)

    @classmethod
    def get_csv_folder_path(cls) -> str:
        """Получить путь к папке CSV"""
        cls.load()
        return f"{cls.get_script_dir_path()}/csv"

    @classmethod
    def get_script_dir_path(cls) -> Path:
        """Получить путь к директории скриптов"""
        cls.load()
        path = Path(__file__).resolve().parent
        for parent in [path] + list(path.parents):
            if (parent / ".git").exists():
                return parent
        raise FileNotFoundError("No .git directory found in script path hierarchy.")
