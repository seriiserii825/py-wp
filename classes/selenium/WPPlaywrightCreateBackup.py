import time
from pathlib import Path

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from rich import print

from classes.selenium.WPPlaywright import WPPlaywright


class WPPlaywrightCreateBackup(WPPlaywright):
    def start(self):
        try:
            self.ensure_logged_in()
            return self.make_backup_in_chrome()
        finally:
            self.close()

    def make_backup_in_chrome(self) -> Path:
        backups_url = f"{self.project_url}/wp-admin/admin.php?page=ai1wm_export"
        self.page.goto(backups_url)
        self.page.wait_for_load_state("networkidle")

        self._find_and_click(".ai1wm-button-export")
        time.sleep(1)
        self._find_and_click("#ai1wm-export-file")

        print("[blue]Creating backup on server...")

        try:
            return self._download_from_link(
                ".ai1wm-modal-container a[download]",
                timeout=1800,
            )
        except PlaywrightTimeoutError as e:
            print(f"[red]Backup error: {e}")
            raise
