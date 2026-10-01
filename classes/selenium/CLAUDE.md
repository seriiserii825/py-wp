# Browser automation (backups via All-in-One WP Migration)

Despite the folder name, everything here uses **Playwright**, not Selenium. Entry points are in `classes/backup/Backup.py` (called from `main_menu/backup_menu.py`).

## Two base implementations

- **`WPPlaywright`** — newer base class (create / download / delete backup). Subclasses: `WPPlaywrightCreateBackup`, `WPPlaywrightDownloadBackup`, `WPPlaywrightDeleteBackup`; each `start()` does `ensure_logged_in()` → work → `close()` in `finally`.
- **`MySelenium`** — older class, still used only for `restore_backup_in_chrome()`. Logs via `print`, not `log`. Restore restarts the browser mid-flow (`_restart_browser()`, old cookies are invalid after a WP restore), so `self.page` changes — anything holding the old page must be recreated.

Both read project url/login/password from `Project(<cwd basename>)` and keep the login session in `sessions/session_<theme>.json`.

## Logging

`log` is defined in `WPPlaywright.py` (`logging.getLogger("WPPlaywright")`, `basicConfig` at import time, level DEBUG): output goes to the terminal (RichHandler) and is appended to `sessions/wp_playwright.log`. Importing `WPPlaywright` (directly or via `WPPlugins`) configures logging for the whole process.

## Backup plugins — `WPPlugins`

All-in-One WP Migration plugins are kept **deactivated** on sites and turned on only for the duration of a backup operation.

- `WPPlugins(page, project_url)` works on `wp-admin/plugins.php`; plugin state is detected by link id: `#activate-<slug>` = inactive, `#deactivate-<slug>` = active, neither = not installed.
- `activate(slugs, optional)` / `deactivate(slugs)` — skip plugins already in the target state; send one `Notification` listing what actually changed.
- A required plugin that isn't installed → `PluginNotInstalledError` + notification (fail fast, before reaching `ai1wm_*` pages). Plugins in `optional` → warning only. Missing plugin on deactivate is never an error.
- `activated(slugs, optional)` — context manager used by the `WPPlaywright*Backup` classes; deactivates in reverse order (extension before base) even if activation or the block raised.
- `BACKUP_PLUGINS` = `all-in-one-wp-migration` (required) + `all-in-one-wp-migration-unlimited-extension` (in `BACKUP_PLUGINS_OPTIONAL` — not every site has it).
- Plugins are deactivated at the end **always**, even if they were active before the run (intended).
- Restore can't use the context manager (browser restart): it calls `activate()` before restoring and, after permalinks are saved, activates `wps-hide-login` / `altuofianco-theme-login` (both optional) and deactivates the backup plugins with a new `WPPlugins` instance.
