from pathlib import Path
from classes.files.AbstractFileCreator import AbstractFileCreator
from classes.files.FileWriter import FileWriter
from classes.files.FilesHandle import FilesHandle
from classes.files.PhpTemplateToFile import PhpTemplateToFile
from classes.utils.Command import Command
from classes.utils.InputValidator import InputValidator


class PHPBlockFileCreator(AbstractFileCreator):
    def get_root_dir(self) -> str:
        return "blocks"

    def get_extension(self) -> str:
        return "php"

    def _file_path(self, path_to_dir) -> str:
        FilesHandle().list_files(path_to_dir, "php")
        file_name = InputValidator.get_string(
            "Enter file name without extension: ")
        file_name = self._remove_extension(file_name)
        file_name = self._clear_whitespaces(file_name)
        file_name = f"{file_name}-block"
        file_name = self._add_extension(file_name, self.get_extension())
        return str(Path(path_to_dir) / file_name)

    def template_to_file(self, file_path: str) -> None:
        file_name = Path(file_path).name
        camel_case_name = self._to_camel_case(file_name)
        camel_case_name = camel_case_name.replace(".php", "")
        camel_case_name = camel_case_name.replace("Block", "")
        keywords = file_name.replace("-block.php", "")
        html = f"""
        <?php
        add_action('acf/init', 'registerBlock{camel_case_name}');

        function registerBlock{camel_case_name}()
        {{
          if (! function_exists('acf_register_block_type')) return;

          acf_register_block_type([
            'name'            => '{camel_case_name}',
            'title'           => __('{camel_case_name}', 'your-textdomain'),
            'description'     => __('A custom {camel_case_name} block.', 'your-textdomain'),
            'render_template' => 'template-parts/home/{file_name}',
            'category'        => 'formatting',
            'icon'            => 'welcome-learn-more',
            'keywords'        => ['{keywords}'],
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
        template_path = file_path
        Command.run(f"bat '{str(Path(template_path).resolve())}'")
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
        Command.run(f"bat '{str(functions_php_path.resolve())}'")
