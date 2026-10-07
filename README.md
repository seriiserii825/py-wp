# WPManager

**WPManager** is a Python CLI tool that helps manage WordPress
installations using `wp-cli`. It simplifies tasks like managing plugins,
controlling Advanced Custom Fields (ACF),
and updating WordPress version info — all from Python scripts.

## Features

- 🧠 Import, export, and manipulate ACF fields (including nested groups)
- ✅ Manage and install plugins via `wp-cli`
- 💾 Backups through wp-admin (All-in-One WP Migration) with Playwright — with a visible browser or headless
- 📋 "Use from list" — actions on any site from `list.csv`, not only the current theme

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

| Argument          | Description                                    |
| ----------------- | ---------------------------------------------- |
| `--to-import`     | Import ACF data from file instead of exporting |
| `--use-from-list` | Directly open the "Use from list" menu         |

```bash
wb                  # export ACF (default)
wb --to-import      # import ACF from file
wb --use-from-list  # open "Use from list"
```

Run `wb --help` for the full list of `--menu-*` shortcuts.

### Main menu

The main menu and the "Use from list" submenu are colored tables
(`Index | Option`): type the option number and press Enter.

### Use from list

Works with sites from `list.csv` (`title,login,password,url[,login_path]`).
A url with a path (`https://site.it/gestione`) is split into the site url and
the login path automatically.

| Option                  | What it does |
| ----------------------- | ------------ |
| Reinstall Altuofianco   | Pick a site (type a domain or search with fzf), choose browser / headless, then in wp-admin: deactivate + delete `disable-comments-altuofianco` and `altuofianco-theme-login` (skipped if not installed), upload the `altuofianco-theme-login` zip from `~/Documents/plugins-wp` (filename from `csv/base-plugins.csv`) and activate it. With a visible browser it waits for Enter at the end so you can check the site. |
| Find project            | fzf over all sites, one line each: `title \| url \| login \| password \| login_path`; prints the picked line. |
| Add credentials to list | Reads 3 lines from the clipboard — domain, login, password. If they are missing/invalid, prints a hint and returns. Otherwise asks for the theme name and appends `theme,login,password,url` to `list.csv` (same rules as `set-theme-in-wp-list-csv.sh`: url reduced to `https://domain`, no duplicates, confirmation if the theme already exists with other data). `list.csv.gpg` is not updated. |

### Browser: visible or headless

Every action that drives wp-admin through Playwright (Reinstall Altuofianco,
Backups: Create on Server / Restore in Browser / Delete in Browser / Download
Last) first asks **Open browser?**:

- **Yes** — visible Chromium window, same behavior as before.
- **No (headless)** — no window, a bit faster. Steps that needed looking at the
  page move to the terminal: the users list is printed as a table and you pick
  users to delete in fzf (Tab, Esc = nobody); backups on the server are printed
  and picked in fzf instead of entering a count.

A login captcha can't be solved headless — use the visible browser for such sites.

---

## Installation

Inside folder run script pm to install dependencies and create a virtual environment:

```bash
https://github.com/seriiserii825/py-wp
cd py-wp
./pm
```
