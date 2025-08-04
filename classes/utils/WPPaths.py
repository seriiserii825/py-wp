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
    PLUGIN_WP_PATH = "plugin_wp_path"
    BACKUPS_PATH = "backups_path"


class WPPaths:
    _paths: Dict[str, str] = {}
    _paths_file: Optional[Path] = None
    _user_dir_path: str = str(Path.home())

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
            PathKey.PLUGIN_WP_PATH.value: f"{cls._user_dir_path}/Documents/plugins-wp",
            PathKey.BACKUPS_PATH.value: str((wp_content / "ai1wm-backups").resolve()),
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

    @classmethod
    def get_plugins_wp_path(cls) -> Path:
        """Получить путь к папке плагинов WordPress"""
        cls.load()
        return cls.get(PathKey.PLUGIN_WP_PATH)

    @classmethod
    def get_theme_path(cls) -> Path:
        """Получить путь к текущей теме WordPress"""
        cls.load()
        return cls.get(PathKey.THEME)

    @classmethod
    def get_backups_path(cls) -> Path:
        """Получить путь к папке резервных копий"""
        cls.load()
        backup_folder_path = cls.get(PathKey.BACKUPS_PATH)
        if not backup_folder_path.exists():
            backup_folder_path.mkdir(parents=True, exist_ok=True)
        return cls.get(PathKey.BACKUPS_PATH)
