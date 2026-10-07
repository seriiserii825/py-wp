import re
import zipfile
from pathlib import Path

from classes.csv.BasePluginsCsv import BasePluginsCsv
from classes.selenium.WPPlaywright import WPPlaywright, log
from classes.selenium.WPPlugins import WPPlugins, BACKUP_PLUGINS
from classes.utils.WPPaths import WPPaths
from py_libs.Notification import Notification

DISABLE_COMMENTS_PLUGIN = "disable-comments-altuofianco"
THEME_LOGIN_PLUGIN = "altuofianco-theme-login"
HIDE_LOGIN_PLUGIN = "wps-hide-login"
# deactivated by hand before the run when it blocked the login — turn it back on
TURNSTILE_PLUGIN_SLUG = "simple-cloudflare-turnstile"
# installed (and left deactivated) when missing — needed for backups
BACKUP_PLUGIN = "all-in-one-wp-migration"


class WPPlaywrightReinstallAltuofianco(WPPlaywright):
    def start(self):
        try:
            # check the zips before touching the site, so a missing file
            # doesn't leave it without a login plugin
            zip_path = self._plugin_zip(THEME_LOGIN_PLUGIN)
            backup_zip_path = self._plugin_zip(BACKUP_PLUGIN)
            self.ensure_logged_in()
            plugins = WPPlugins(self.page, self.project_url, relogin=self.relogin)

            # a rerun shouldn't reinstall the same version again
            zip_version = self._zip_version(zip_path)
            installed_version = plugins.installed_version(THEME_LOGIN_PLUGIN)
            # unknown zip version → can't compare, reinstall to be safe
            reinstall = zip_version is None or installed_version != zip_version
            log.info(
                f"{THEME_LOGIN_PLUGIN}: installed {installed_version or 'none'}, "
                f"zip {zip_version} → {'reinstall' if reinstall else 'up to date, skipping'}"
            )
            install_backup = not plugins.is_installed(BACKUP_PLUGIN)

            # check BEFORE deleting anything: without the upload form the site
            # would be left without the login plugin
            if (reinstall or install_backup) and not plugins.can_upload():
                message = (
                    f"No 'Upload plugin' on {self.project_url} — plugin installs are "
                    "blocked (NinjaFirewall / DISALLOW_FILE_MODS?). Nothing was changed."
                )
                log.error(message)
                Notification(title="Reinstall Altuofianco stopped", message=message).notify()
                raise SystemExit(1)

            # old standalone plugin, now part of altuofianco-theme-login
            if not plugins.delete(DISABLE_COMMENTS_PLUGIN):
                log.info(f"{DISABLE_COMMENTS_PLUGIN} not installed, nothing to remove")
            if reinstall:
                if not plugins.delete(THEME_LOGIN_PLUGIN):
                    log.info(f"{THEME_LOGIN_PLUGIN} not installed, nothing to remove")
                plugins.upload(zip_path)
                plugins.activate_after_upload()
            # verify on plugins.php: active plugins have #deactivate-<slug>
            plugins.activate([THEME_LOGIN_PLUGIN])
            if install_backup:
                log.info(f"{BACKUP_PLUGIN} not installed, installing (stays deactivated)")
                plugins.upload(backup_zip_path)
            # final state of the site: backup plugins off (extension before
            # its base plugin), login hidden
            plugins.deactivate(list(reversed(BACKUP_PLUGINS)))
            # optional: a site without it gets a warning, not an abort
            plugins.activate([HIDE_LOGIN_PLUGIN], optional=[HIDE_LOGIN_PLUGIN])
            # only if installed: most sites don't have it
            plugins.activate([TURNSTILE_PLUGIN_SLUG], optional=[TURNSTILE_PLUGIN_SLUG])
            if self.headless:
                log.info(f"Done, check: {self.project_url}/wp-admin/plugins.php")
            else:
                input("Check the site, then press Enter to close the browser...")
        finally:
            self.close()

    @staticmethod
    def _zip_version(zip_path: Path) -> str | None:
        """`Version:` from the plugin header of <slug>/<slug>.php inside the zip."""
        slug = THEME_LOGIN_PLUGIN
        with zipfile.ZipFile(zip_path) as zf:
            header = zf.read(f"{slug}/{slug}.php").decode(errors="ignore")[:4096]
        match = re.search(r"^\s*\*?\s*Version:\s*(\S+)", header, re.MULTILINE)
        return match.group(1) if match else None

    @staticmethod
    def _plugin_zip(slug: str) -> Path:
        """Zip filename comes from csv/base-plugins.csv, so a version bump there
        is picked up here too."""
        for dto in BasePluginsCsv().get_plugin_dtos():
            if dto.plugin_slug == slug:
                zip_path = Path(WPPaths.get_plugins_wp_path()) / dto.filename
                if not zip_path.exists():
                    raise FileNotFoundError(f"Plugin zip not found: {zip_path}")
                return zip_path
        raise RuntimeError(f"{slug} not found in base-plugins.csv")
