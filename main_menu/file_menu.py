from pathlib import Path

from classes.files.FileCreatorFactory import FileCreatorFactory
from classes.files.FilesHandle import FilesHandle
from classes.files.ModuleFileCreator import ModuleFileCreator
from classes.utils.InputValidator import InputValidator
from classes.utils.ModuleSystemDetector import ModuleSystemDetector
from classes.utils.Select import Select
from main_menu.file_type_menu import file_type_menu
from rich import print


def file_menu():
    is_modules = ModuleSystemDetector.detect()

    if is_modules:
        print("[bold green]✓ Module system detected[/bold green]")
    else:
        print("[bold yellow]Standard system detected[/bold yellow]")

    if not InputValidator.get_bool_true_default("Continue? (Enter/n): "):
        return

    if is_modules:
        _module_menu()
    else:
        _standard_menu()


def _standard_menu():
    file_type = file_type_menu()
    if file_type.name == "NONE":
        return
    try:
        file = FileCreatorFactory.get_creator(file_type)
        file_path = file.create_file(use_dir=file_type.use_dir)
        file.template_to_file(file_path)
    except Exception as e:
        print(f"[red]Error: {e} in file_menu.py[/red]")
        exit(1)


def _module_menu():
    module_path = FilesHandle().create_or_choose_directory("modules")
    print(f"[green]Module: {module_path}[/green]")

    selected = Select.select_with_fzf(["php", "scss", "js", "phps", "api", "Back"])
    if not selected:
        return
    file_type = selected[0]
    if file_type == "Back":
        return

    preset_name = None
    if file_type == "scss":
        module_name = Path(module_path).name
        scss_exists = (Path(module_path) / f"{module_name}.scss").exists()
        if not scss_exists:
            print(f"[yellow]No SCSS file found for module '{module_name}'.[/yellow]")
            print("[blue]Create new one?.")
            choice = Select.select_with_fzf([module_name, "other"])
            if choice and choice[0] == module_name:
                preset_name = module_name

    creator = ModuleFileCreator(module_path, file_type, preset_name=preset_name)
    file_path = creator.create_file(use_dir=False)
    creator.template_to_file(file_path)
