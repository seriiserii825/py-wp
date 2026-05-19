import time
from pathlib import Path

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from classes.selenium.WPPlaywright import WPPlaywright, log


class WPPlaywrightCreateBackup(WPPlaywright):
    def start(self):
        try:
            self.ensure_logged_in()
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

        try:
            return self._download_from_link(
                ".ai1wm-modal-container a[download]",
                timeout=1800,
            )
        except PlaywrightTimeoutError as e:
            log.error(f"Backup error: {e}")
            raise
