from pathlib import Path

from classes.files.AbstractFileCreator import AbstractFileCreator
from classes.files.FileWriter import FileWriter
from classes.files.FilesHandle import FilesHandle
from classes.utils.Command import Command
from classes.utils.InputValidator import InputValidator


class PHPApiFileCreator(AbstractFileCreator):
    def __init__(self) -> None:
        self._func_name: str = ""
        self._route: str = ""

    def get_root_dir(self) -> str:
        return "api"

    def get_extension(self) -> str:
        return "php"

    def _file_path(self, path_to_dir: str) -> str:
        FilesHandle().list_files(path_to_dir, "php")
        self._func_name = InputValidator.get_string("Function name (e.g. adsFilterView): ")
        self._route = InputValidator.get_string("Route (e.g. ads-filter-view): ")
        file_name = self._func_name_to_kebab(self._func_name) + "-api"
        file_name = self._add_extension(file_name, self.get_extension())
        return str(Path(path_to_dir) / file_name)

    def template_to_file(self, file_path: str) -> None:
        content = self._build_template(self._func_name, self._route)
        FileWriter.write_file(Path(file_path), content)
        Command.run(f"bat '{Path(file_path).resolve()}'")
        self.append_to_functions_php(file_path)

    @staticmethod
    def append_to_functions_php(file_path: str) -> None:
        functions_php = Path("functions.php")
        if not functions_php.exists():
            print(f"functions.php not found, skipping include")
            return
        include = f'require_once get_template_directory() . "/{file_path}";\n'
        content = functions_php.read_text()
        if include not in content:
            with open(functions_php, "a") as f:
                f.write("\n" + include)
            Command.run(f"bat '{functions_php.resolve()}'")
        else:
            print(f"{include.strip()} already exists in functions.php")

    @staticmethod
    def _func_name_to_kebab(name: str) -> str:
        import re
        s = re.sub(r"([A-Z])", r"-\1", name).lstrip("-").lower()
        return s

    @staticmethod
    def _build_template(func_name: str, route: str) -> str:
        return (
            "<?php\n"
            "if (!defined('ABSPATH')) exit;\n"
            "\n"
            f"function {func_name}Api()\n"
            "{\n"
            f"  register_rest_route('site/v1', '/{route}', [\n"
            "    'methods'             => WP_REST_SERVER::READABLE,\n"
            "    'permission_callback' => '__return_true',\n"
            f"    'callback' => '{func_name}ApiData',\n"
            "  ]);\n"
            "}\n"
            f"add_action('rest_api_init', '{func_name}Api');\n"
            "\n"
            f"function {func_name}ApiData()\n"
            "{\n"
            "  $data = [];\n"
            "\n"
            "  return rest_ensure_response($data);\n"
            "}\n"
        )
