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
    LIST_CSV = "list_csv"


class WPPaths:
    _paths: Dict[str, str] = {}
    _paths_file: Optional[Path] = None
    _user_dir_path: Path = Path.home()

    # ---------- bootstrap-safe helpers ----------
    @classmethod
    def _get_script_dir(cls) -> Path:
        """Directory of this file (classes/utils)."""
        return Path(__file__).resolve().parent

    @classmethod
    def _resolve_repo_root_or_script_dir(cls) -> Path:
        """
        Find the git repo root (first parent with .git) starting from this file.
        Fallback to this file's parent if no repo root is found.
        NOTE: This function is safe to call before initialize() and DOES NOT call load.
        """
        start = cls._get_script_dir()
        for parent in [start] + list(start.parents):
            if (parent / ".git").exists():
                return parent
        return start

    @classmethod
    def _ensure_paths_file(cls) -> Path:
        """
        Set the paths file path. Do NOT create/touch it here to avoid empty file reads.
        """
        if cls._paths_file is None:
            cls._paths_file = cls._get_script_dir() / ".paths.json"
        return cls._paths_file

    # ---------- public API ----------
    @classmethod
    def initialize(cls, base_dir: Optional[Path] = None):
        """Compute paths and write .paths.json (idempotent)."""
        paths_file = cls._ensure_paths_file()

        if base_dir is None:
            base_dir = Path.cwd()

        # themes/lm-omp → wp-content (adjust if your structure differs)
        wp_content = base_dir.parent.parent

        # IMPORTANT: do not call get_script_dir_path() here (it calls load()).
        script_dir_path = cls._resolve_repo_root_or_script_dir()

        cls._paths = {
            PathKey.BASE.value: str(base_dir.resolve()),
            PathKey.WP_CONTENT.value: str(wp_content.resolve()),
            PathKey.UPLOADS.value: str((wp_content / "uploads").resolve()),
            PathKey.PLUGINS.value: str((wp_content / "plugins").resolve()),
            PathKey.THEME.value: str(base_dir.resolve()),
            PathKey.SCRIPT_DIR.value: str(script_dir_path),
            PathKey.PLUGIN_WP_PATH.value: str(
                cls._user_dir_path / "Documents/plugins-wp"
            ),
            PathKey.BACKUPS_PATH.value: str((wp_content / "ai1wm-backups").resolve()),
            PathKey.LIST_CSV.value: str((script_dir_path / "list.csv").resolve()),
        }

        # Write atomically to avoid partial/empty file states
        tmp = paths_file.with_suffix(".paths.json.tmp")
        tmp.write_text(json.dumps(cls._paths, indent=2), encoding="utf-8")
        tmp.replace(paths_file)

    @classmethod
    def load(cls):
        """Load paths from .paths.json (tolerant to empty/corrupt files)."""
        paths_file = cls._ensure_paths_file()

        if cls._paths:
            return  # already loaded

        if not paths_file.exists() or paths_file.stat().st_size == 0:
            # Not initialized yet; keep in-memory empty dict
            cls._paths = {}
            return

        try:
            cls._paths = json.loads(paths_file.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            # Corrupted file — treat as uninitialized
            cls._paths = {}

    @classmethod
    def get(cls, key: PathKey) -> Path:
        """Get a stored path by key."""
        cls.load()
        try:
            return Path(cls._paths[key.value])
        except KeyError as e:
            raise KeyError(
                f"Key '{key.value}' not found. Have you called WPPaths.initialize()?"
            ) from e

    @classmethod
    def get_plugin_path(cls) -> Path:
        return cls.get(PathKey.PLUGINS)

    @classmethod
    def get_csv_folder_path(cls) -> Path:
        """Get path to CSV folder (based on script dir)."""
        # Use the public method but ensure it's safe:
        return cls.get_script_dir_path() / "csv"

    @classmethod
    def get_script_dir_path(cls) -> Path:
        """
        Public accessor for the script/repo dir.
        After initialization, prefers the stored value;
        otherwise resolves without load loop.
        """
        # Try stored value first
        cls.load()
        stored = cls._paths.get(PathKey.SCRIPT_DIR.value)
        if stored:
            return Path(stored)

        # If not initialized yet, resolve directly without touching load()
        return cls._resolve_repo_root_or_script_dir()

    @classmethod
    def get_plugins_wp_path(cls) -> Path:
        return cls.get(PathKey.PLUGIN_WP_PATH)

    @classmethod
    def get_theme_path(cls) -> Path:
        return cls.get(PathKey.THEME)

    @classmethod
    def get_backups_path(cls) -> Path:
        backup_folder_path = cls.get(PathKey.BACKUPS_PATH)
        backup_folder_path.mkdir(parents=True, exist_ok=True)
        return backup_folder_path

    @classmethod
    def get_list_csv_path(cls) -> Path:
        return cls.get(PathKey.LIST_CSV)
