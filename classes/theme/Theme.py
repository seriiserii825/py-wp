from pathlib import Path
from classes.utils.Command import Command
from classes.utils.Select import Select
from classes.utils.WPPaths import WPPaths


class Theme:
    @staticmethod
    def list_all():
        Command.run("wp theme list")

    @staticmethod
    def _get_themes_from_wp() -> list[str]:
        theme_path = WPPaths.get_theme_path()
        one_folder_up = Path(theme_path).parent
        themes = []
        for theme in one_folder_up.iterdir():
            if theme.is_dir() and (theme / "style.css").exists():
                themes.append(theme.name)
        return themes

    @classmethod
    def install_theme(cls):
        cls.list_all()
        theme_to_install = cls._search_theme()
        Command.run("wp theme install " + theme_to_install + " --activate")

    @classmethod
    def _search_theme(cls) -> str:
        theme_to_search = input("Enter the theme name to search: ").strip()
        themes_json = Command.run_json(
            "wp theme search " + theme_to_search + " --format=json"
        )
        themes = [theme["slug"] for theme in themes_json]
        return Select.select_with_fzf(themes)[0]

    @classmethod
    def activate_theme(cls):
        cls.list_all()
        wp_themes = cls._get_themes_from_wp()
        themes = Select.select_multiple(wp_themes)
        Command.run("wp theme activate " + themes[0])

    @classmethod
    def deactivate_theme(cls):
        cls.list_all()
        theme = Select.select_with_fzf(cls._get_themes_from_wp())
        Command.run("wp theme deactivate " + theme[0])

    @classmethod
    def delete_theme(cls):
        cls.list_all()
        themes = Select.select_multiple(cls._get_themes_from_wp())
        for value in themes:
            Command.run("wp theme delete " + value)
