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
`main.py` shows a top-level menu dispatching to modules in `main_menu/`. Each `main_menu/*.py` file handles a feature domain (ACF, plugins, files, pages, etc.).

### Path Configuration
`classes/utils/WPPaths.py` is a central singleton managing all project-relative paths, persisted in `.paths.json`. All file operations should use `WPPaths.get(PathType.X)` rather than hardcoded paths.

### ACF Module
The most complex subsystem (`classes/acf/`):

- **`EFieldType`** (enum) — 12 field types: text, textarea, image, gallery, file, group, repeater, tab, true_false, post_object, message, wysiwyg
- **`FieldDTO`** — dataclass carrying field metadata through the pipeline
- **`FieldBuilder`** — interactive CLI prompts (questionary/fzf) to collect field data
- **`FieldCreator`** — orchestrates FieldBuilder → FieldTemplateFactory
- **`FieldFactory`** — Python 3.10+ `match/case` factory mapping `EFieldType` → concrete `Field` subclasses
- **`Field`** (abstract base) — in `abc_dir/Field.py`; concrete implementations in `fields_dir/`
- **`AcfTransfer`** — wp-cli wrapper for JSON export/import

Fields that contain sub-fields (GROUP, REPEATER) override `Field` with recursive handling.

### Command Execution
`classes/utils/Command.py` wraps all subprocess/wp-cli calls:
- `Command.run()` — execute with Rich output
- `Command.run_quiet()` — execute silently, return stdout
- `Command.run_json()` — execute and parse JSON output
- `Command.build()` — shell-escape arguments

### File Creation
`classes/files/FileCreatorFactory.py` is a factory for file type creators (PHP, PHPBlock, SCSS, JS, etc.) all implementing `FileCreatorInterface`.

### DTOs
Global DTOs live in `dto/`. Module-local DTOs (e.g., `FieldDTO`) live alongside their module.

## Key Patterns

- **Factory + match/case**: `FieldFactory`, `FileCreatorFactory` use Python 3.10+ structural pattern matching
- **Abstract base classes**: Field types, file creators use ABC
- **Facade**: `ContactForm`, `AcfTransfer` wrap underlying service classes
- **Interactive menus**: `classes/utils/Menu.py`, `Select.py`, `simple-term-menu`, `pyfzf`, `questionary`
- **Type safety**: mypy is enforced; run `mypy .` before committing
