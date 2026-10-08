import time
from pathlib import Path

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from rich.console import Console

from classes.selenium.WPPlaywright import WPPlaywright, log
from classes.selenium.WPPlugins import WPPlugins, BACKUP_PLUGINS, BACKUP_PLUGINS_OPTIONAL

DOWNLOAD_LINK = ".ai1wm-modal-container a[download]"
EXPORT_TIMEOUT_SECONDS = 1800


class WPPlaywrightCreateBackup(WPPlaywright):
    def start(self):
        try:
            self.ensure_logged_in()
            with WPPlugins(self.page, self.project_url, relogin=self.relogin).activated(BACKUP_PLUGINS, BACKUP_PLUGINS_OPTIONAL):
                return self.make_backup_in_chrome()
        finally:
            self.close()

    def make_backup_in_chrome(self) -> Path:
        backups_url = f"{self.project_url}/wp-admin/admin.php?page=ai1wm_export"
        log.info(f"Navigating to export page: {backups_url}")
        self.page.goto(backups_url)
        self.page.wait_for_load_state("load")
        log.debug(f"Current URL after goto: {self.page.url}")

        self._find_and_click(".ai1wm-button-export")
        time.sleep(1)
        self._find_and_click("#ai1wm-export-file")

        log.info("Creating backup on server...")
        self._show_export_progress()

        try:
            return self._download_from_link(DOWNLOAD_LINK, timeout=10)
        except PlaywrightTimeoutError as e:
            log.error(f"Backup error: {e}")
            raise

    def _show_export_progress(self) -> None:
        """Status line with the export modal text (e.g. "Archiving files... 45%") until the download link shows up."""
        started = time.monotonic()
        last_text = ""
        with Console().status("Creating backup on server...") as status:
            while True:
                elapsed = int(time.monotonic() - started)
                if elapsed > EXPORT_TIMEOUT_SECONDS:
                    raise PlaywrightTimeoutError(
                        f"Backup not ready after {EXPORT_TIMEOUT_SECONDS} s (last status: {last_text!r})"
                    )
                if self.page.locator(DOWNLOAD_LINK).first.is_visible():
                    break
                text = " ".join(self.page.evaluate(
                    "() => document.querySelector('.ai1wm-modal-container')?.innerText || ''"
                ).split())
                if text:
                    last_text = text
                status.update(f"[{elapsed // 60:02d}:{elapsed % 60:02d}] {last_text or 'Creating backup on server...'}")
                time.sleep(1)
        log.info(f"Backup created on server in {elapsed // 60:02d}:{elapsed % 60:02d}")
