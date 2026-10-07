from pathlib import Path

from classes.csv.BasePluginsCsv import BasePluginsCsv
from classes.selenium.WPPlaywright import WPPlaywright, log
from classes.selenium.WPPlugins import WPPlugins, BACKUP_PLUGINS
from classes.utils.WPPaths import WPPaths
from py_libs.Notification import Notification

DISABLE_COMMENTS_PLUGIN = "disable-comments-altuofianco"
THEME_LOGIN_PLUGIN = "altuofianco-theme-login"
HIDE_LOGIN_PLUGIN = "wps-hide-login"


class WPPlaywrightReinstallAltuofianco(WPPlaywright):
    def start(self):
        try:
            # check the zip before touching the site, so a missing file
            # doesn't leave it without a login plugin
            zip_path = self._theme_login_zip()
            if not zip_path.exists():
                raise FileNotFoundError(f"Plugin zip not found: {zip_path}")
            self.ensure_logged_in()
            plugins = WPPlugins(self.page, self.project_url, relogin=self.relogin)
            # check BEFORE deleting anything: without the upload form the site
            # would be left without the login plugin
            if not plugins.can_upload():
                message = (
                    f"No 'Upload plugin' on {self.project_url} — plugin installs are "
                    "blocked (NinjaFirewall / DISALLOW_FILE_MODS?). Nothing was changed."
                )
                log.error(message)
                Notification(title="Reinstall Altuofianco stopped", message=message).notify()
                raise SystemExit(1)
            for slug in (DISABLE_COMMENTS_PLUGIN, THEME_LOGIN_PLUGIN):
                if not plugins.delete(slug):
                    log.info(f"{slug} not installed, nothing to remove")
            plugins.upload(zip_path)
            plugins.activate_after_upload()
            # verify on plugins.php: active plugins have #deactivate-<slug>
            plugins.activate([THEME_LOGIN_PLUGIN])
            # final state of the site: backup plugins off (extension before
            # its base plugin), login hidden
            plugins.deactivate(list(reversed(BACKUP_PLUGINS)))
            # optional: a site without it gets a warning, not an abort
            plugins.activate([HIDE_LOGIN_PLUGIN], optional=[HIDE_LOGIN_PLUGIN])
            if self.headless:
                log.info(f"Done, check: {self.project_url}/wp-admin/plugins.php")
            else:
                input("Check the site, then press Enter to close the browser...")
        finally:
            self.close()

    @staticmethod
    def _theme_login_zip() -> Path:
        """Zip filename comes from csv/base-plugins.csv, so a version bump there
        is picked up here too."""
        for dto in BasePluginsCsv().get_plugin_dtos():
            if dto.plugin_slug == THEME_LOGIN_PLUGIN:
                return Path(WPPaths.get_plugins_wp_path()) / dto.filename
        raise RuntimeError(f"{THEME_LOGIN_PLUGIN} not found in base-plugins.csv")
