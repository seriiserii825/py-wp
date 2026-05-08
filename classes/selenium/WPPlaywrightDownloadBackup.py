import time
from pathlib import Path

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from rich import print

from classes.selenium.WPPlaywright import WPPlaywright


class WPPlaywrightDownloadBackup(WPPlaywright):
    def start(self):
        try:
            self.ensure_logged_in()
            return self.download_last_backup_from_server()
        finally:
            self.close()

    def download_last_backup_from_server(self) -> Path:
        backups_url = f"{self.project_url}/wp-admin/admin.php?page=ai1wm_backups"
        self.page.goto(backups_url)
        self.page.wait_for_load_state("networkidle")

        self._find_and_click(
            "table.ai1wm-backups tbody tr .ai1wm-backup-dots",
            index=0,
            js=True,
        )
        time.sleep(1)

        print("[blue]Downloading latest backup from server...")

        try:
            return self._download_from_link(
                '.ai1wm-backup-dots-menu[style*="block"] a[download]',
                index=0,
            )
        except PlaywrightTimeoutError as e:
            print(f"[red]Download error: {e}")
            raise
