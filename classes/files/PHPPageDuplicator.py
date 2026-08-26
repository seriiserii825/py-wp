from rich import print

from classes.files.FileWriter import FileWriter
from classes.utils.Command import Command
from classes.utils.InputValidator import InputValidator
from classes.utils.Select import Select
from classes.utils.WPPaths import WPPaths


class PHPPageDuplicator:
    @staticmethod
    def duplicate() -> None:
        theme_dir = WPPaths.get_theme_path()
        php_files = sorted(
            f.name for f in theme_dir.iterdir() if f.is_file() and f.suffix == ".php"
        )
        if not php_files:
            print("[yellow]No PHP files found in theme root.[/yellow]")
            return

        selected = Select.select_fzf_one([*php_files, "Back", "Exit"])
        if not selected or selected == "Back":
            return
        if selected == "Exit":
            print("Exiting the program. Goodbye!")
            exit(0)

        source_path = theme_dir / selected

        file_name = InputValidator.get_string(
            "Enter new file name without extension: "
        )
        file_name = file_name.strip().replace(" ", "-")
        if file_name.endswith(".php"):
            file_name = file_name[: -len(".php")]
        new_path = theme_dir / f"{file_name}.php"

        if new_path.exists():
            overwrite = InputValidator.get_bool(
                "File already exists. Overwrite? (y/n): "
            )
            if not overwrite:
                print("Aborted.")
                return

        FileWriter.write_file(new_path, source_path.read_text())
        print(f"[green]Duplicated '{selected}' -> '{new_path.name}'[/green]")
        Command.run(f"bat '{str(new_path.resolve())}'")
