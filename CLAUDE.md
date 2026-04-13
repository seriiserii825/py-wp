# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**py-wp** is a Python CLI tool for managing WordPress installations via `wp-cli`. It handles ACF (Advanced Custom Fields) management, plugin installation, page/theme management, file creation, backups, and contact form analysis.

**Requirements:** Python >= 3.10, `wp-cli` in PATH.

## Development Commands

```bash
# Run the CLI
python main.py

# Install dependencies (via uv)
./pm

# Type checking
mypy .

# Lint
flake8 .

# Format
autopep8 --in-place <file>
```

The `pm` script is an interactive bash menu for package management (install/uninstall packages via `uv`, run mypy, manage pre-commit hooks).

## Architecture

### Entry Point
`main.py` calls `WPPaths.initialize()` first (required before any path access), then shows a top-level fzf menu dispatching to modules in `main_menu/`. Each `main_menu/*.py` file handles a feature domain (ACF, plugins, files, pages, etc.).

### Path Configuration
`classes/utils/WPPaths.py` manages all project-relative paths as a class with class methods, persisted in `.paths.json`. Use `WPPaths.get(PathKey.X)` (not `PathType`) — the enum is `PathKey`. Must call `WPPaths.initialize()` once at startup before any `get()` calls.

### ACF Module (`classes/acf/`)
The most complex subsystem, split into two concerns:

**Field management** (`classes/acf/field/`):
- **`EFieldType`** (enum) — 12 types: TEXT, TEXTAREA, WYSIWYG, IMAGE, GALLERY, FILE, TRUE_FALSE, TAB, GROUP, REPEATER, MESSAGE, POST_OBJECT
- **`FieldDTO`** (`field/dto/`) — dataclass carrying field metadata through the pipeline
- **`FieldBuilder`** — interactive CLI prompts (questionary/fzf) to collect field data; converts label → name automatically
- **`FieldCreator`** — orchestrates FieldBuilder → FieldTemplateFactory; handles TAB specially (returns list of dicts: tab + optional group)
- **`FieldFactory`** (`field/factories/`) — `create_field(field_data)` maps `EFieldType` → concrete `Field` subclasses using `match/case`; used for **display/reading** existing fields
- **`FieldTemplateFactory`** (`field/factories/`) — converts `FieldDTO` → ACF-compatible `dict`; used for **creating** new fields for JSON export. Outputs dicts, NOT Field instances.
- **`Field`** ABC (`field/abc_dir/Field.py`) — concrete implementations in `field/fields_dir/`. GROUP and REPEATER hold `sub_fields` lists and recurse.
- **`FieldRepository`** — JSON persistence (load/save from `acf/*.json`)

**Section management** (`classes/acf/section/`):
- **`CreateSection`** — builds ACF field group JSON: asks for name and type (Page, CPT, Taxonomy, Options Page, Block), builds location rules, writes to `acf/*.json` using `Generate.get_group_id()`
- **`EditSection`**, **`SelectSection`**, **`SectionMenu`** — CRUD UI for field groups

**`AcfTransfer`** — wp-cli wrapper: `wp_export()` runs `wp acf export --all`, `wp_import()` runs `wp acf clean` then `wp acf import --all`.

### Command Execution
`classes/utils/Command.py` wraps all subprocess/wp-cli calls:
- `Command.run()` — execute with Rich output
- `Command.run_quiet()` — execute silently, return stdout
- `Command.run_json()` — execute and parse JSON output
- `Command.build()` — shell-escape arguments

`classes/data/WpData.py` provides static methods wrapping `os.popen()` for reading WordPress data: `get_wp_pages()`, `get_wp_posts()`, `get_wp_taxonomies()`, `get_acf_options_pages()` (parses theme's `inc/acf.php`).

### File Creation
`classes/files/FileCreatorFactory.py` is a factory for file type creators using `match/case` on `FileTypeEnum` (in `enum_folder/`). All creators extend `AbstractFileCreator` which implements `FileCreatorInterface`. The abstract base handles interactive directory navigation and filename prompting; concrete classes (`PHPFileCreator`, `PHPBlockFileCreator`, `SCSSFileCreator`, `JsFileCreator`, etc.) define `get_root_dir()`, `get_extension()`, and `template_to_file()`.

`PHPBlockFileCreator` additionally generates ACF block registration code and appends an include to `functions.php`.

### DTOs
Global DTOs live in `dto/`. Module-local DTOs (e.g., `FieldDTO`) live alongside their module in `classes/acf/field/dto/`.

## Key Patterns

- **Factory + match/case**: `FieldFactory`, `FieldTemplateFactory`, `FileCreatorFactory` all use Python 3.10+ structural pattern matching
- **Two-factory ACF design**: `FieldFactory` creates `Field` instances (for display); `FieldTemplateFactory` creates `dict` (for JSON export) — these are distinct and not interchangeable
- **Abstract base classes**: `Field`, `AbstractFileCreator`, `FileCreatorInterface`, `PluginAbc`
- **Facade**: `ContactForm` (static methods), `AcfTransfer` wrap underlying service classes
- **Interactive menus**: `classes/utils/Menu.py` (`select_fzf()`), `Select.py`, `simple-term-menu`, `pyfzf`, `questionary`
- **JSON-based ACF persistence**: ACF data lives in `acf/*.json` files; wp-cli imports/exports to the WordPress database — no direct DB access
- **Type safety**: mypy is enforced; run `mypy .` before committing
