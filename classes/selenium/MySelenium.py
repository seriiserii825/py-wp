import os
import time
from pathlib import Path
from urllib.parse import urlparse
from rich import print

from playwright.sync_api import (
    sync_playwright,
    Page,
    Browser,
    BrowserContext,
    TimeoutError as PlaywrightTimeoutError,
)

from classes.projects.Project import Project


SESSIONS_DIR = Path(__file__).resolve().parent.parent.parent / "sessions"
SESSIONS_DIR.mkdir(exist_ok=True)


class MySelenium:
    def __init__(self):
        self.download_dir = str(Path.home() / "Downloads")
        self._playwright = sync_playwright().start()

        current_dir_path = os.getcwd()
        self.theme_name = os.path.basename(current_dir_path)
        self.session_path = str(SESSIONS_DIR / f"session_{self.theme_name}.json")

        self.pr = Project(self.theme_name)
        self.project = self.pr.getProject()
        self.project_login = self.project["login"]
        self.project_password = self.project["password"]
        self.project_url = self.project["url"]
        self.sitem_login = self.pr.getLoginUrl(False)

        self._launch_browser()

    def _launch_browser(self, *, fresh: bool = False) -> None:
        self._browser: Browser = self._playwright.chromium.launch(headless=False)
        session_file = Path(self.session_path)
        if not fresh and session_file.exists():
            print(f"[dim]Loading saved session: {self.session_path}[/dim]")
            self.context: BrowserContext = self._browser.new_context(
                storage_state=self.session_path,
                accept_downloads=True,
            )
        else:
            self.context = self._browser.new_context(accept_downloads=True)
        self.page: Page = self.context.new_page()

    def _restart_browser(self) -> None:
        """Close current browser and relaunch with a fresh context — needed after WordPress restore."""
        try:
            self.context.close()
        except Exception:
            pass
        try:
            self._browser.close()
        except Exception:
            pass
        self._launch_browser(fresh=True)

    def _save_session(self) -> None:
        self.context.storage_state(path=self.session_path)
        print(f"[dim]Session saved → {self.session_path}[/dim]")

    def _find_login_url(self) -> str | None:
        """Try login URLs in order, return the first one that shows the login form."""
        candidates = [
            self.sitem_login,
            f"{self.project_url}/wp-admin",
            f"{self.project_url}/gestione",
            f"{self.project_url}/login",
        ]
        for url in candidates:
            for attempt in range(10):
                try:
                    self.page.goto(url)
                    break
                except Exception:
                    if attempt == 9:
                        raise
                    print(f"[dim]    server not ready, retrying in 5s... ({attempt + 1}/10)[/dim]")
                    time.sleep(5)
            self._wait_for_captcha()
            if self.page.locator("#user_login").count() > 0:
                return url
        return None

    def _click_through_db_upgrade(self) -> None:
        """Click through the WordPress DB upgrade page if currently on it (no-op otherwise)."""
        if "upgrade.php" not in self.page.url:
            return
        print("[dim]>>> DB upgrade page, clicking upgrade button[/dim]")
        self.page.locator("a.button-primary").first.wait_for(state="visible", timeout=10_000)
        self.page.locator("a.button-primary").first.click()
        self.page.wait_for_load_state("load")

        if "upgrade.php" in self.page.url:
            print("[dim]>>> Upgrade done page, clicking Continua[/dim]")
            continua = self.page.locator("a.button:not(.button-primary)")
            if continua.count() > 0:
                continua.first.click()
                self.page.wait_for_load_state("load")

    def _login(self, check_login_element: bool = False):
        """Navigate to login page, handle captcha, and submit credentials."""
        self.page.goto(f"{self.project_url}/wp-admin")
        self._click_through_db_upgrade()
        if "/wp-admin" in self.page.url and "wp-login" not in self.page.url:
            return

        login_url = self._find_login_url()
        if login_url is None:
            raise RuntimeError(
                f"Login form not found. Tried: {self.sitem_login}, "
                f"{self.project_url}/wp-admin, {self.project_url}/gestione, "
                f"{self.project_url}/login"
            )

        if check_login_element:
            self._go_next_if_no_login_element()

        self.page.fill("#user_login", self.project_login)
        self.page.fill("#user_pass", self.project_password)
        self.page.click("#wp-submit")

        self.page.wait_for_url(
            lambda url: "/wp-admin" in url and "wp-login" not in url,
            timeout=30_000,
        )
        self._save_session()

    def _find_and_click(self, css: str, *, index: int = 0, timeout: int = 10, js: bool = False) -> None:
        idx_label = "last" if index == -1 else f"#{index}"
        print(f"[dim]>>> searching {idx_label} [{css}][/dim]")

        locator = self.page.locator(css)
        locator.first.wait_for(state="visible", timeout=timeout * 1_000)

        count = locator.count()
        print(f"[dim]    found {count} element(s)[/dim]")

        element = locator.last if index == -1 else locator.nth(index)

        tag = element.evaluate("el => el.tagName.toLowerCase()")
        text = (element.inner_text() or "").strip()[:40] or element.get_attribute("class") or ""
        print(f"[dim]    clicking <{tag}> '{text}'[/dim]")

        if js:
            element.dispatch_event("click")
        else:
            element.click(timeout=30_000)

        print(f"[dim]    clicked[/dim]")

    def _get_visible_link_target(self, css: str, *, index: int = 0, timeout: int = 10) -> tuple[str, str]:
        """Return href and filename from a visible download link."""
        idx_label = "last" if index == -1 else f"#{index}"
        print(f"[dim]>>> resolving link {idx_label} [{css}][/dim]")

        locator = self.page.locator(css)
        locator.first.wait_for(state="visible", timeout=timeout * 1_000)
        element = locator.last if index == -1 else locator.nth(index)

        href = element.get_attribute("href")
        if not href:
            raise RuntimeError(f"Link has no href for selector: {css}")

        filename = (
            element.get_attribute("download")
            or Path(urlparse(href).path).name
            or "download.bin"
        )
        print(f"[dim]    href: {href}[/dim]")
        print(f"[dim]    filename: {filename}[/dim]")
        return href, filename

    def _download_from_link(self, css: str, *, index: int = 0, timeout: int = 10):
        """Trigger browser download using the resolved href instead of a synthetic DOM click."""
        href, fallback_filename = self._get_visible_link_target(css, index=index, timeout=timeout)

        with self.page.expect_download(timeout=3_600_000) as download_info:
            self.page.evaluate("url => window.location.assign(url)", href)

        download = download_info.value
        downloads_page = self.context.new_page()
        downloads_page.goto("chrome://downloads/")

        suggested_filename = download.suggested_filename or fallback_filename
        save_path = Path(self.download_dir) / suggested_filename
        download.save_as(str(save_path))
        print(f"Бэкап успешно загружен: {save_path}")
        return save_path

    def _close(self) -> None:
        try:
            self.context.close()
        except Exception:
            pass
        try:
            self._browser.close()
        except Exception:
            pass
        self._playwright.stop()

    def _wait_for_captcha(self, timeout: int = 60):
        try:
            self.page.wait_for_selector(
                ".aiowps-captcha-answer", state="visible", timeout=1_000
            )
            self.page.wait_for_selector(
                ".aiowps-captcha-answer", state="hidden", timeout=timeout * 1_000
            )
        except PlaywrightTimeoutError:
            return

    def _go_next_if_no_login_element(self):
        if self.page.locator("#user_login").count() > 0:
            print("Login element exists")
        else:
            go_next = input("Go next? [y/n]: ")
            if go_next == "y":
                print("Go next")
            else:
                exit(1)

    def _handle_db_upgrade_if_needed(self) -> None:
        """Click through upgrade.php then navigate back to options-permalink.php if needed."""
        self._click_through_db_upgrade()
        if "options-permalink.php" not in self.page.url:
            print("[dim]>>> Navigating back to options-permalink.php[/dim]")
            self.page.goto(f"{self.project_url}/wp-admin/options-permalink.php")
            self.page.wait_for_load_state("load")

    def _handle_post_permalink_redirect(self) -> None:
        """Handle redirects that can occur after saving permalinks.

        After a restore, WordPress may redirect through:
          1. upgrade.php?step=1  → click the DB-upgrade button
          2. upgrade.php (done)  → click "Continua"
          3. wp-login.php        → log in again
        """
        self.page.wait_for_load_state("load")
        self._click_through_db_upgrade()
        current = self.page.url

        if "wp-login.php" in current:
            print("[dim]>>> Login page after permalink save, re-authenticating[/dim]")
            self.page.fill("#user_login", self.project_login)
            self.page.fill("#user_pass", self.project_password)
            self.page.click("#wp-submit")
            self.page.wait_for_url(
                lambda url: "/wp-admin" in url and "wp-login" not in url,
                timeout=30_000,
            )
            self._save_session()
            print("[dim]>>> Re-login after permalink save successful[/dim]")

    def make_backup_in_chrome(self):
        self._login()
        backups_url = f"{self.project_url}/wp-admin/admin.php?page=ai1wm_export"
        self.page.goto(backups_url)

        self._find_and_click(".ai1wm-button-export")
        time.sleep(1)
        self._find_and_click("#ai1wm-export-file")

        print("Начинается загрузка бэкапа...")

        try:
            return self._download_from_link(
                ".ai1wm-modal-container a[download]",
                timeout=1800,
            )
        except PlaywrightTimeoutError as e:
            print(f"Ошибка: {e}")
            raise
        finally:
            self._close()

    def restore_backup_in_chrome(self):
        self._login(check_login_element=True)
        backups_url = f"{self.project_url}/wp-admin/admin.php?page=ai1wm_backups"
        self.page.goto(backups_url)

        agree_to_delete = input("[red]Do you want to delete existing backups? [y/n]: ")
        if agree_to_delete == "y":
            self.choose_backups_to_delete()
        else:
            print("Not deleting existing backups")

        self._find_and_click("table.ai1wm-backups tbody tr .ai1wm-backup-dots", index=0, js=True)
        time.sleep(2)
        self._find_and_click(
            '.ai1wm-backup-dots-menu[style*="block"] .ai1wm-backup-restore',
            index=0, js=True
        )
        time.sleep(1)
        self._find_and_click(".ai1wm-import-modal-actions .ai1wm-button-green", timeout=30)

        # Wait for restore to complete — can take a long time
        self.page.wait_for_selector(
            ".ai1wm-import-modal-content-done", timeout=3_600_000
        )
        time.sleep(1)

        # WordPress restarts after restore — relaunch with fresh context (old cookies invalid)
        time.sleep(3)
        self._restart_browser()

        self._login(check_login_element=True)

        save_permalink_url = f"{self.project_url}/wp-admin/options-permalink.php"
        self.page.goto(save_permalink_url)
        self.page.wait_for_load_state("load")
        self._handle_db_upgrade_if_needed()
        self.page.locator("#submit").click()
        self._handle_post_permalink_redirect()

        plugins_url = f"{self.project_url}/wp-admin/plugins.php"
        self.page.goto(plugins_url)
        self._find_and_click("#activate-wps-hide-login")

        self._close()

    def download_last_backup_from_server(self):
        self._login()
        backups_url = f"{self.project_url}/wp-admin/admin.php?page=ai1wm_backups"
        self.page.goto(backups_url)

        self._find_and_click("table.ai1wm-backups tbody tr .ai1wm-backup-dots", index=0, js=True)
        time.sleep(1)

        print("Начинается загрузка последнего бэкапа с сервера...")

        try:
            return self._download_from_link(
                '.ai1wm-backup-dots-menu[style*="block"] a[download]',
                index=0,
            )
        except PlaywrightTimeoutError as e:
            print(f"Ошибка: {e}")
            raise
        finally:
            self._close()

    def delete_backup_in_chrome(self):
        self._login()
        backups_url = f"{self.project_url}/wp-admin/admin.php?page=ai1wm_backups"
        self.page.goto(backups_url)
        self.choose_backups_to_delete()

    def choose_backups_to_delete(self):
        number_of_backups = input("[green]Enter number of backups to delete: ").strip()
        if not number_of_backups:
            exit("[red]Number of backups is empty!")

        try:
            num_backups = int(number_of_backups)
        except ValueError:
            exit("[red]Please enter a valid number!")

        print(f"Number of backups: {num_backups}")

        for i in range(num_backups):
            try:
                self._find_and_click(
                    "table.ai1wm-backups tr .ai1wm-backup-dots", index=-1, js=True
                )
                time.sleep(2)

                self.page.once("dialog", lambda dialog: dialog.accept())
                self._find_and_click(
                    '.ai1wm-backup-dots-menu[style*="block"] .ai1wm-backup-delete',
                    index=0, js=True
                )

                time.sleep(2)
                print(f"[green]Deleted backup {i + 1} of {num_backups}")

            except (PlaywrightTimeoutError, RuntimeError) as e:
                print(f"[red]Error deleting backup {i + 1}: {e}")
                raise
