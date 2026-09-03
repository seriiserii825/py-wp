from pathlib import Path

from classes.files.FileCreatorFactory import FileCreatorFactory
from classes.files.FilesHandle import FilesHandle
from classes.files.ModuleFileCreator import ModuleFileCreator
from classes.utils.InputValidator import InputValidator
from classes.utils.ModuleSystemDetector import ModuleSystemDetector
from classes.utils.Select import Select
from main_menu.file_type_menu import file_type_menu
from rich import print


def _to_camel_case(name: str) -> str:
    parts = name.split("-")
    return parts[0] + "".join(
        word[0].upper() + word[1:] if word else "" for word in parts[1:]
    )


def file_menu():
    is_modules = ModuleSystemDetector.detect()

    if is_modules:
        print("[bold green]✓ Module system detected[/bold green]")
    else:
        print("[bold yellow]Standard system detected[/bold yellow]")

    if not InputValidator.confirm("Continue?"):
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

    file_types = ["api", "icon", "js", "php", "phps", "scss", "Back"]
    numbered_types = [f"{i + 1:02d}.{t}" for i, t in enumerate(file_types)]
    selected = Select.select_with_fzf(numbered_types)
    if not selected:
        return
    file_type = file_types[numbered_types.index(selected[0])]
    if file_type == "Back":
        return

    preset_name = None
    module_name = Path(module_path).name

    if file_type == "php":
        if not (Path(module_path) / f"{module_name}.php").exists():
            print(
                f"[yellow]No PHP file found for module '{module_name}'.[/yellow]")
            print(f"[dim]Enter file name (Enter = '{module_name}'):[/dim]")
            name = input("  ").strip()
            preset_name = name if name else module_name

    elif file_type == "scss":
        if not (Path(module_path) / f"{module_name}.scss").exists():
            print(
                f"[yellow]No SCSS file found for module '{module_name}'.[/yellow]")
            print(f"[dim]Enter file name (Enter = '{module_name}'):[/dim]")
            name = input("  ").strip()
            preset_name = name if name else module_name

    elif file_type == "phps":
        php_missing = not (Path(module_path) / f"{module_name}.php").exists()
        scss_missing = not (Path(module_path) / f"{module_name}.scss").exists()
        if php_missing or scss_missing:
            missing = " + ".join(
                ext for ext, m in [("PHP", php_missing), ("SCSS", scss_missing)] if m
            )
            print(
                f"[yellow]Missing: {missing} for module '{module_name}'.[/yellow]")
            print(
                f"[dim]Enter file name for both (Enter = '{module_name}'):[/dim]")
            name = input("  ").strip()
            preset_name = name if name else module_name

    elif file_type == "js":
        is_animation = InputValidator.confirm("Is this an animation file?")
        if is_animation:
            preset_name = f"{_to_camel_case(module_name)}Animation"
        else:
            print(f"[dim]Enter file name (Enter = '{module_name}'):[/dim]")
            name = input("  ").strip()
            preset_name = name if name else module_name

    creator = ModuleFileCreator(
        module_path, file_type, preset_name=preset_name)
    file_path = creator.create_file(use_dir=False)
    creator.template_to_file(file_path)
