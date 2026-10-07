# Browser automation (backups via All-in-One WP Migration, plugin reinstall)

Despite the folder name, everything here uses **Playwright**, not Selenium. Entry points are in `classes/backup/Backup.py` (called from `main_menu/backup_menu.py`).

## Two base implementations

- **`WPPlaywright`** — newer base class (create / download / delete backup). Subclasses: `WPPlaywrightCreateBackup`, `WPPlaywrightDownloadBackup`, `WPPlaywrightDeleteBackup`; each `start()` does `ensure_logged_in()` → work → `close()` in `finally`.
- **`MySelenium`** — older class, still used only for `restore_backup_in_chrome()`. Logs via `print`, not `log`. Restore restarts the browser mid-flow (`_restart_browser()`, old cookies are invalid after a WP restore), so `self.page` changes — anything holding the old page must be recreated.

Both read project url/login/password from `Project(<cwd basename>)` and keep the login session in `sessions/session_<theme>.json`. `WPPlaywright(theme_name=...)` takes a `list.csv` title to work on another site (used by Use from list).

Browser contexts are created with `ignore_https_errors=True`: some sites have no own SSL cert (the server answers with the hosting's cert, e.g. `vps6.bludelego.com` → `ERR_CERT_COMMON_NAME_INVALID`), which a regular browser lets you click through but Playwright fails on.

Contexts also get a regular Chrome `user_agent` (`browser_user_agent()`): headless Chromium identifies as `HeadlessChrome/…`, and NinjaFirewall answers that with `403 Forbidden` on every page — looks like "Login form not found on any candidate URL".

The form is submitted by `submit_login()` (`WPPlaywright.py`, shared with `MySelenium`). If the login page has **Cloudflare Turnstile** (`.cf-turnstile`, plugin "Simple CAPTCHA with Cloudflare Turnstile") it raises `TurnstileBlockedError` before filling anything: Turnstile never passes in a Playwright browser, not even by hand in the visible window (checked: `navigator.webdriver` true, widget height 0, no `cf-turnstile-response` token, submit does nothing). `run_browser_flow()` (`main_menu/ask_open_browser.py`) reports it — log + notification "deactivate the plugin 'Simple CAPTCHA with Cloudflare Turnstile' in wp-admin and run again" — and exits; the flow's `finally` / `MySelenium._close()` already closed the browser. (The dark "Login form protected by WPS Limit Login" box is just that plugin's credit line, not the blocker.)

Login form is searched at `login_candidates()` (`WPPlaywright.py`, shared with `MySelenium`): the list.csv login path, then `/wp-admin`, `/gestione`, `/login`, `/login.php`, `/wp-login.php`. A candidate that redirects straight into wp-admin counts as "already logged in".

"Already logged in" is detected by `body.wp-admin` on the page, NOT by the url — a 404 under `/wp-admin` (e.g. from a wrong url) also contains `/wp-admin`. Both base classes use this check.

## Headless mode

`WPPlaywright(headless=...)` / `MySelenium(headless=...)`, default `False`; stored as `self.headless`. The menu asks via `main_menu/ask_open_browser.py`. When headless:
- `goToUsers()` doesn't wait for Enter in the browser; it uses **`WPUsers`** (`WPUsers.py`): reads `users.php` (all pages), prints a table, fzf-multi to pick users to delete, `y/n` confirm, deletes via each row's delete link; if the user has content, asks delete content vs. attribute to the preselected user.
- Deleting backups uses **`AI1WMBackups`** (`AI1WMBackups.py`) instead of "enter a count": prints the `ai1wm_backups` table, fzf-multi, `y/n`, deletes the picked rows by filename (waits for each row to detach).
- `chrome://downloads` isn't opened after a download.
With a visible browser both steps behave as before (browser pause / count prompt).

## Logging

`log` is defined in `WPPlaywright.py` (`logging.getLogger("WPPlaywright")`, `basicConfig` at import time, level DEBUG): output goes to the terminal (RichHandler) and is appended to `sessions/wp_playwright.log`. Importing `WPPlaywright` (directly or via `WPPlugins`) configures logging for the whole process.

## Backup plugins — `WPPlugins`

All-in-One WP Migration plugins are kept **deactivated** on sites and turned on only for the duration of a backup operation.

- `WPPlugins(page, project_url, relogin=...)` works on `wp-admin/plugins.php`; plugin state is detected by link id: `#activate-<slug>` = inactive, `#deactivate-<slug>` = active, neither = not installed.
- `_open()` verifies it really is the plugins page (`body.plugins-php`). Some sites drop the session mid-run (seen right after deactivating `all-in-one-wp-migration`; the login-hider then answers `/404/`, which would otherwise read as "plugin not installed"). With `relogin` (`WPPlaywright.relogin` / `MySelenium._relogin`, both return the site url) it logs in once more and retries; without it, or if that fails too, it raises. Always pass `relogin`.
- Navigation goes through `_goto()`, which retries `net::ERR_ABORTED` (3×, 2 s). Seen on sites whose WordPress address (Settings → General) is `http://` while they run on https: after an admin action WP redirects to http, the https-only login cookies aren't sent, the login-hider answers `/404/` (looks logged out), and the next https `goto` gets aborted. The https session is still valid — `_log_where()` warns about the http redirect, the flow continues over https.
- After every click (toggle, delete, upload, activate-after-upload) `_log_where()` logs a DEBUG line with the resulting url and whether still logged in — use it to see which step loses the session.
- `activate(slugs, optional)` / `deactivate(slugs)` — skip plugins already in the target state; send one `Notification` listing what actually changed.
- A required plugin that isn't installed → `PluginNotInstalledError` + notification (fail fast, before reaching `ai1wm_*` pages). Plugins in `optional` → warning only. Missing plugin on deactivate is never an error.
- `activated(slugs, optional)` — context manager used by the `WPPlaywright*Backup` classes; deactivates in reverse order (extension before base) even if activation or the block raised.
- `BACKUP_PLUGINS` = `all-in-one-wp-migration` (required) + `all-in-one-wp-migration-unlimited-extension` (in `BACKUP_PLUGINS_OPTIONAL` — not every site has it).
- Plugins are deactivated at the end **always**, even if they were active before the run (intended).
- `delete(slug)` — deactivate if active, then click `#delete-<slug>` (accepts the confirm dialog, waits for the ajax removal); returns `False` if not installed.
- `upload(zip_path)` — opens `plugin-install.php?tab=upload` directly (form already shown, no `.upload-view-toggle` click; page checked by `body.plugin-install-php` with the same re-login as `_open`, clear error if `#pluginzip` is missing) → `set_input_files("#pluginzip")` (no OS dialog) → Install now; fails if the result page has no activate link. `activate_after_upload()` clicks that link.
- Restore can't use the context manager (browser restart): it calls `activate()` before restoring and, after permalinks are saved, activates `wps-hide-login` / `altuofianco-theme-login` (both optional) and deactivates the backup plugins with a new `WPPlugins` instance.

## Reinstall Altuofianco — `WPPlaywrightReinstallAltuofianco`

Started from Use from list for a chosen `list.csv` site. Safe to rerun (a run often has to be repeated after a site-side hiccup). Order:
1. Both zips (`altuofianco-theme-login`, `all-in-one-wp-migration`; filenames from `csv/base-plugins.csv`, folder `WPPaths.get_plugins_wp_path()`) must exist — checked **before** touching the site.
2. Login.
3. Version check: installed `altuofianco-theme-login` version from its row on `plugins.php` (`WPPlugins.installed_version()`, "Versione 1.1.0 | Di …") vs `Version:` in the zip's plugin header (`_zip_version()`). Equal → skip delete/upload for it (rerun-safe); different, not installed or zip version unreadable → reinstall.
4. Only if something will be uploaded (reinstall, or `all-in-one-wp-migration` missing): `can_upload()` — upload form missing (NinjaFirewall, `DISALLOW_FILE_MODS`) → error + notification + `SystemExit(1)`, nothing changed.
5. `delete` `disable-comments-altuofianco` (old standalone plugin, always); if reinstall: `delete` + `upload` + `activate_after_upload()` `altuofianco-theme-login`.
6. `activate(["altuofianco-theme-login"])` — check/ensure active.
7. `all-in-one-wp-migration` not installed → `upload()` its zip (left deactivated).
8. `deactivate` both `BACKUP_PLUGINS` (extension first) → `wps-hide-login`: not installed → `install_from_wordpress_org()` (Add plugin search → "Install now", it's `wps-hide-login,False` in base-plugins.csv — no zip), then `activate` (required) → `activate(["simple-cloudflare-turnstile"])` (optional — re-enables Turnstile the user deactivated to let the tool log in).
9. Visible browser: wait for Enter; headless: log the `plugins.php` link.
