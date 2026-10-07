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

**`AcfTransfer`** — wp-cli wrapper. `wp_export()` runs `wp acf export --all` then re-sorts the exported `acf/*.json` files by `menu_order`. `wp_import()` does more than a plain `wp acf clean` + `wp acf import --all`: ACF's own export/import does NOT preserve field order (`menu_order` is always `None`/absent in exported JSON, and `wp acf import` won't reorder fields that already exist in the DB). So `wp_import()` also (1) applies the stored field order from `acf-snapshots/*.json` onto each `acf/*.json` via `AcfSnapshotService.reorder_from_snapshot()` before importing, and (2) after import, pushes that order into `wp_posts.menu_order` directly via `AcfTransfer.push_menu_order_to_db()` (runs `bash-scripts/json-acf-menu-order.sh`, one direct SQL `UPDATE` per field group) — this is the only thing that actually changes what the WP admin displays.

**`AcfSnapshotService`** (`classes/acf/AcfSnapshotService.py`) — tracks the *intended* field order separately from `acf/*.json`, in `<theme>/acf-snapshots/<group-slug>.json` (slug derived from the group title). `save()` writes the snapshot FROM the current `acf/*.json` order (one-way, used to bootstrap/refresh a snapshot — never call this expecting it to apply order, it does the opposite of `reorder_from_snapshot`). `reorder_from_snapshot()` reads the snapshot and reorders a single `acf/*.json` group's fields to match it (recursing into `sub_fields`), matching fields by `name`/`label`, not `key` — so two fields sharing the same `name` will collide and one will silently drop out of the result.

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

### Main menu style
The top-level menu (`main.py`) and `main_menu/use_from_list_menu.py` use the **table** menu, not fzf: `Menu.display(title, ["Index", "Option"], rows, row_styles=...)` + `Menu.choose_option()`. Main-menu colors are computed: `bold red` for Init / Reset Settings / Exit, otherwise alternating `bold blue` / `bold green` by index — adding an item needs no manual recoloring. Each menu item that should be reachable directly gets a `--flag` in `main.py` (e.g. `--use-from-list`) and a matching `menu_*` kwarg of `menu()`.

### Use from list (`main_menu/use_from_list_menu.py`)
Actions on any site from `list.csv`, not the cwd theme:
- **Reinstall Altuofianco** — site picked by domain substring (input → filter `url`; several matches → fzf) or fzf over all; then `WPPlaywrightReinstallAltuofianco(title, headless=...)`. Returns to the Use from list menu when done.
- **Find project** — fzf over one-line `title | url | login | password | gestione`, prints the pick.
- **Add credentials to list** (`main_menu/add_credentials_to_list.py`) — Python port of `~/Documents/bash/bash-scripts/set-theme-in-wp-list-csv.sh`. Clipboard is read and validated FIRST (3 lines: url, login, password); only if invalid is the hint printed. Then asks the theme name and appends to `list.csv`. Doesn't touch `list.csv.gpg` / `.sha256`.
- **Copy credentials** — `_select_project()`, then `Clipboard.write(password, show=False)`, `COPY_DELAY_SECONDS` (1 s) pause so the clipboard manager records both, `Clipboard.write(login)`.
- **Change credentials** (`main_menu/change_credentials_in_list.py`) — fzf over the RAW `list.csv` lines (not `Project.get_all_projects()`, which normalizes urls), table of fields with current values, new value validated (no commas; url → origin; empty login path drops column 5), `y/n`, then only that line is replaced in the file.

`Project.get_all_projects()` (`classes/projects/Project.py`) is the `list.csv` reader for anything that USES a site (only the list-editing menus read raw lines). It normalizes urls stored with a login path (`https://site.it/gestione` → url `https://site.it`, `gestione` = `gestione` unless column 5 sets it) — anything building `{url}/wp-admin` relies on that.

`main_menu/ask_open_browser.py` → `ask_open_browser()` is the shared "Open browser?" table prompt (True = visible, False = headless); used by Use from list and the browser items of the Backups menu. Every browser flow is started through `run_browser_flow(run, headless)` from the same module: if the login page has Cloudflare Turnstile (`TurnstileBlockedError` from `submit_login()`), it logs + notifies "log in yourself, deactivate the plugin 'Simple CAPTCHA with Cloudflare Turnstile' and run again" and exits (`SystemExit(1)`). Reinstall Altuofianco re-activates `simple-cloudflare-turnstile` at the end if installed. Turnstile can't be passed from a Playwright browser even by hand (`navigator.webdriver` is true, widget height 0, no token) — don't try to wait for the user or rerun with the window open, and don't hide the automation flag. New browser menu items must go through `run_browser_flow()` too.

### Browser Backups
Backup create/download/delete/restore through wp-admin (Playwright, All-in-One WP Migration plugins toggled on/off around each run) live in `classes/selenium/` — details in `classes/selenium/CLAUDE.md`. All browser flows support headless mode; the interactive steps (users review, picking backups to delete) then run in the terminal.

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
