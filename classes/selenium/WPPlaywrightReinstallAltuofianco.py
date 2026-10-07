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
            reinstall = self._needs_install(plugins, THEME_LOGIN_PLUGIN, zip_path)
            backup_installed = plugins.is_installed(BACKUP_PLUGIN)
            install_backup = self._needs_install(plugins, BACKUP_PLUGIN, backup_zip_path)

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
                # its uninstall only drops ai1wm options; backup files stay on the server
                if backup_installed:
                    plugins.delete(BACKUP_PLUGIN)
                plugins.upload(backup_zip_path)  # left deactivated
            for slug, path in ((THEME_LOGIN_PLUGIN, zip_path), (BACKUP_PLUGIN, backup_zip_path)):
                self._check_version(plugins, slug, path)
            # final state of the site: backup plugins off (extension before
            # its base plugin), login hidden
            plugins.deactivate(list(reversed(BACKUP_PLUGINS)))
            # login must end up hidden: install it when the site doesn't have it
            if not plugins.is_installed(HIDE_LOGIN_PLUGIN):
                plugins.install_from_wordpress_org(HIDE_LOGIN_PLUGIN)
            plugins.activate([HIDE_LOGIN_PLUGIN])
            # only if installed: most sites don't have it
            plugins.activate([TURNSTILE_PLUGIN_SLUG], optional=[TURNSTILE_PLUGIN_SLUG])
            if self.headless:
                log.info(f"Done, check: {self.project_url}/wp-admin/plugins.php")
            else:
                input("Check the site, then press Enter to close the browser...")
        finally:
            self.close()

    def _needs_install(self, plugins: WPPlugins, slug: str, zip_path: Path) -> bool:
        """True if the installed version differs from the zip's (or the plugin is
        missing, or the zip version can't be read — then reinstall to be safe)."""
        zip_version = self._zip_version(zip_path, slug)
        installed = plugins.installed_version(slug)
        needed = zip_version is None or installed != zip_version
        log.info(
            f"{slug}: installed {installed or 'none'}, zip {zip_version} → "
            f"{'install' if needed else 'up to date, skipping'}"
        )
        return needed

    def _check_version(self, plugins: WPPlugins, slug: str, zip_path: Path) -> None:
        zip_version = self._zip_version(zip_path, slug)
        installed = plugins.installed_version(slug)
        if zip_version and installed != zip_version:
            log.warning(f"{slug}: expected {zip_version}, site has {installed or 'none'}")

    @staticmethod
    def _zip_version(zip_path: Path, slug: str) -> str | None:
        """`Version:` from the plugin header of <slug>/<slug>.php inside the zip."""
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
