from pathlib import Path
import re
from classes.files.AbstractFileCreator import AbstractFileCreator
from classes.files.FileWriter import FileWriter
from classes.files.FilesHandle import FilesHandle
from classes.utils.Command import Command
from classes.utils.InputValidator import InputValidator


class PHPBlockFileCreator(AbstractFileCreator):
    def get_root_dir(self) -> str:
        return "blocks"

    def get_extension(self) -> str:
        return "php"

    def _file_path(self, path_to_dir) -> str:
        dir_path = FilesHandle().create_or_choose_directory(path_to_dir)
        FilesHandle().list_files(dir_path, "php")
        file_name = InputValidator.get_string(
            "Enter file name without extension, -block will be added: ")
        file_name = f"{file_name}-block"
        file_name = self._remove_extension(file_name)
        file_name = self._clear_whitespaces(file_name)
        file_name = self._add_extension(file_name, self.get_extension())
        return str(Path(dir_path) / file_name)

    def template_to_file(self, file_path: str) -> None:
        # blocks/footer/our-services.php: file_path from phpblock
        file_path_without_extension = self._remove_extension(file_path)
        print(f"file_path_without_extension: {file_path_without_extension}")
        file_path_without_block = file_path_without_extension.removeprefix("blocks/")
        file_path_without_block = file_path_without_block.replace("-block", "")
        file_name = Path(file_path).name
        file_name_without_extension = self._remove_extension(file_name)
        camel_case_name = self._to_camel_case(file_name)
        camel_case_name = camel_case_name.replace(".php", "")
        camel_case_name = camel_case_name.replace("Block", "")
        name_with_spaces = self.camel_to_spaced(camel_case_name)
        keywords = self.normalize_words(name_with_spaces.lower())
        html = f"""<?php
add_action('acf/init', 'registerBlock{camel_case_name}');

function registerBlock{camel_case_name}()
{{
  if (! function_exists('acf_register_block_type')) return;

  acf_register_block_type([
    'name'            => '{file_name_without_extension}',
    'title'           => '{name_with_spaces}',
    'description'     => 'A custom {name_with_spaces} block.',
    'render_template' => 'template-parts/{file_path_without_block}.php',
    'category'        => 'formatting',
    'icon'            => 'welcome-learn-more',
    'keywords'        => [{keywords}],
    'supports'        => [
      'align'  => False,
      'anchor' => False,
      'mode'   => True,
      'jsx'    => False,
    ],
  ]);
}}

        """
        FileWriter.write_file(Path(file_path), html)
        Command.run(f"bat '{Path(file_path)}'")
        self.append_to_functions_php(file_path)

    def _to_camel_case(self, file_name: str) -> str:
        parts = file_name.split("-")
        camel_case_name = "".join(part.capitalize() for part in parts)
        return camel_case_name

    def append_to_functions_php(self, file_path: str) -> None:
        functions_php_path = Path("functions.php")
        include = f'require_once get_template_directory() . "/{file_path}";\n'
        content = functions_php_path.read_text()
        if include not in content:
            with open(functions_php_path, "a") as f:
                f.write("\n" + include)
        else:
            print(f"{include} already exists in functions.php")

    def camel_to_spaced(self, text: str) -> str:
        return re.sub(r'(?<!^)(?=[A-Z])', ' ', text)

    def normalize_words(self, spaced: str) -> str:
        if ' ' in spaced:
            spaced = ', '.join(map(lambda w: f"'{w}'", spaced.split(' ')))
        else:
            spaced = f"'{spaced}'"
        return spaced
