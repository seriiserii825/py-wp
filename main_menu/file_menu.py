from pathlib import Path

from classes.files.FileCreatorFactory import FileCreatorFactory
from py_libs.FilesHandle import FilesHandle
from classes.files.ModuleFileCreator import ModuleFileCreator
from py_libs.InputValidator import InputValidator
from classes.utils.ModuleSystemDetector import ModuleSystemDetector
from enum_folder.FileTypeEnum import FileTypeEnum
from main_menu.file_type_menu import file_type_menu
from main_menu.table_menu import BACK, table_menu
from rich import print


def _to_camel_case(name: str) -> str:
    parts = name.split("-")
    return parts[0] + "".join(
        word[0].upper() + word[1:] if word else "" for word in parts[1:]
    )


def file_menu(module_dir_mode: str | None = None):
    """module_dir_mode: "create" / "select" skips the Select/Create prompt
    for the module directory (module system only)."""
    is_modules = ModuleSystemDetector.load()

    if is_modules is None:
        is_modules = ModuleSystemDetector.detect()

        if is_modules:
            print("[bold green]✓ Module system detected[/bold green]")
        else:
            print("[bold yellow]Standard system detected[/bold yellow]")

        if not InputValidator.confirm("Continue?"):
            return

        ModuleSystemDetector.save(is_modules)

    if is_modules:
        _module_menu(module_dir_mode)
    else:
        _standard_menu()


def _standard_menu():
    file_type = file_type_menu()
    if file_type.name == "NONE":
        return
    _create_from_factory(file_type)


def _create_from_factory(file_type: FileTypeEnum):
    try:
        file = FileCreatorFactory.get_creator(file_type)
        file_path = file.create_file(use_dir=file_type.use_dir)
        file.template_to_file(file_path)
    except Exception as e:
        print(f"[red]Error: {e} in file_menu.py[/red]")
        exit(1)


def _choose_module_dir(module_dir_mode: str | None) -> str:
    files = FilesHandle()
    if module_dir_mode is None:
        return files.create_or_choose_directory("modules")

    modules_dir = files.ensure_dir("modules")
    files.list_dir(modules_dir)
    has_dirs = any(p.is_dir() for p in Path(modules_dir).iterdir())

    if module_dir_mode == "select" and has_dirs:
        return str(Path(modules_dir) / files.choose_dir(modules_dir))

    dir_name = InputValidator.get_string("Enter directory name: ")
    module_path = Path(modules_dir) / dir_name
    if module_path.exists():
        print(f"[red]Directory '{dir_name}' already exists.[/red]")
        exit(1)
    module_path.mkdir(parents=True)
    print("[green]Directory created[/green]")
    return str(module_path)


def _module_menu(module_dir_mode: str | None = None):
    module_path = _choose_module_dir(module_dir_mode)
    print(f"[green]Module: {module_path}[/green]")
    FilesHandle().list_files(module_path)

    file_types = ["api", "icon", "js", "php", "phps", "scss", "svg"]
    choice = table_menu("File type", file_types)
    if choice == BACK:
        return
    file_type = file_types[choice]

    if file_type == "svg":
        _create_from_factory(FileTypeEnum.SVGI)
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
        animation_name = f"{_to_camel_case(module_name)}Animation"
        animation_exists = any(
            (Path(module_path) / f"{animation_name}.{ext}").exists()
            for ext in ("ts", "js")
        )
        if not animation_exists and InputValidator.confirm(
                "Is this an animation file?"):
            preset_name = animation_name
        else:
            print(f"[dim]Enter file name (Enter = '{module_name}'):[/dim]")
            name = input("  ").strip()
            preset_name = name if name else module_name

    creator = ModuleFileCreator(
        module_path, file_type, preset_name=preset_name)
    file_path = creator.create_file(use_dir=False)
    creator.template_to_file(file_path)
