# WPManager

**WPManager** is a Python CLI tool that helps manage WordPress
installations using `wp-cli`. It simplifies tasks like managing plugins,
controlling Advanced Custom Fields (ACF),
and updating WordPress version info — all from Python scripts.

## Features

- 🧠 Import, export, and manipulate ACF fields (including nested groups)
- ✅ Manage and install plugins via `wp-cli`

---

## Requirements

- Python >= 3.10
- `wp-cli` installed and accessible in your system's PATH

---

## Usage

### Alias setup

```bash
dir_path="/home/serii/Documents/python/py-wp"
alias wb="${dir_path}/.venv/bin/python3 ${dir_path}/main.py"
```

### CLI arguments

| Argument | Description |
|---|---|
| `--to-import` | Import ACF data from file instead of exporting |

```bash
wb              # export ACF (default)
wb --to-import  # import ACF from file
```

---

## Installation

Inside folder run script pm to install dependencies and create a virtual environment:

```bash
https://github.com/seriiserii825/py-wp
cd py-wp
./pm
```
