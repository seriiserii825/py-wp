import time

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from classes.selenium.WPPlaywright import WPPlaywright, log


class WPPlaywrightDeleteBackup(WPPlaywright):
    def start(self):
        try:
            self.ensure_logged_in()
            self.delete_backup_in_chrome()
        finally:
            self.close()

    def delete_backup_in_chrome(self):
        backups_url = f"{self.project_url}/wp-admin/admin.php?page=ai1wm_backups"
        log.info(f"Navigating to backups page: {backups_url}")
        self.page.goto(backups_url)
        self.page.wait_for_load_state("load")
        log.debug(f"Current URL after goto: {self.page.url}")
        self._choose_backups_to_delete()

    def _choose_backups_to_delete(self):
        number_of_backups = input("Enter number of backups to delete: ").strip()
        if not number_of_backups:
            exit("Number of backups is empty!")

        try:
            num_backups = int(number_of_backups)
        except ValueError:
            exit("Please enter a valid number!")

        log.info(f"Deleting {num_backups} backup(s)...")

        for i in range(num_backups):
            try:
                self._find_and_click(
                    "table.ai1wm-backups tr .ai1wm-backup-dots", index=-1, js=True
                )
                time.sleep(2)

                self.page.once("dialog", lambda dialog: dialog.accept())
                self._find_and_click(
                    '.ai1wm-backup-dots-menu[style*="block"] .ai1wm-backup-delete',
                    index=0,
                    js=True,
                )
                time.sleep(2)
                log.info(f"Deleted backup {i + 1} of {num_backups}")

            except (PlaywrightTimeoutError, RuntimeError) as e:
                log.error(f"Error deleting backup {i + 1}: {e}")
                raise
