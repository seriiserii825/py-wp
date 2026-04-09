import os
import re
import subprocess
from pathlib import Path
import time
from rich import print

import requests
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from classes.projects.Project import Project


def _check_chrome_versions():
    def get_version(cmd: list[str]) -> str | None:
        try:
            out = subprocess.check_output(cmd, stderr=subprocess.DEVNULL).decode()
            match = re.search(r"(\d+)\.\d+\.\d+\.\d+", out)
            return match.group(1) if match else None
        except Exception:
            return None

    chrome = get_version(["google-chrome-stable", "--version"])
    driver = get_version(["/usr/bin/chromedriver", "--version"])

    if chrome is None or driver is None:
        print(
            "[yellow]Warning: could not determine Chrome/ChromeDriver versions[/yellow]"
        )
        return

    if chrome != driver:
        raise RuntimeError(
            f"Chrome version ({chrome}) does not match ChromeDriver version ({driver}). "
            "Update chromedriver to fix this."
        )


class MySelenium:
    def __init__(self):
        _check_chrome_versions()
        self.service = Service(executable_path="/usr/bin/chromedriver")
        self.download_dir = str(Path.home() / "Downloads")
        self.options = webdriver.ChromeOptions()
        self.options.add_argument(
            f"user-data-dir={Path.home()}/.config/google-chrome/My-profile"
        )  # Path to your chrome profile

        self.driver = webdriver.Chrome(service=self.service, options=self.options)
        current_dir_path = os.getcwd()
        self.theme_name = os.path.basename(current_dir_path)
        self.pr = Project(self.theme_name)
        self.project = self.pr.getProject()
        self.project_login = self.project["login"]
        self.project_password = self.project["password"]
        self.project_url = self.project["url"]
        self.sitem_login = self.pr.getLoginUrl(False)

    def _find_login_url(self) -> str | None:
        """Try login URLs in order, return the first one that shows the login form."""
        candidates = [
            self.sitem_login,
            f"{self.project_url}/wp-admin",
            f"{self.project_url}/gestione",
            f"{self.project_url}/login",
        ]
        for url in candidates:
            self.driver.get(url)
            self.waitForCaptcha()
            if self.driver.find_elements(By.ID, "user_login"):
                return url
        return None

    def _login(self, check_login_element: bool = False):
        """Navigate to login page, handle captcha, and submit credentials."""
        # Check if already logged in
        self.driver.get(f"{self.project_url}/wp-admin")
        if (
            "/wp-admin" in self.driver.current_url
            and "wp-login" not in self.driver.current_url
        ):
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

        self.driver.find_element(By.ID, "user_login").send_keys(self.project_login)
        self.driver.find_element(By.ID, "user_pass").send_keys(self.project_password)
        self.driver.find_element(By.ID, "wp-submit").click()

        # Wait until login completes and wp-admin is loaded
        WebDriverWait(self.driver, 30).until(
            lambda d: "/wp-admin" in d.current_url and "wp-login" not in d.current_url
        )

    def is_download_complete(self, timeout=3600):
        """
        Проверяет завершение загрузки файла в Chrome.
        Ожидает пока не исчезнут .crdownload файлы.

        Args:
            timeout: максимальное время ожидания в секундах (по умолчанию 1 час)
        """
        download_path = Path(self.download_dir)
        end_time = time.time() + timeout

        while time.time() < end_time:
            temp_files = list(download_path.glob("*.crdownload"))
            tmp_files = list(download_path.glob("*.tmp"))

            if not temp_files and not tmp_files:
                time.sleep(2)
                return True

            if temp_files:
                for f in temp_files:
                    size = f.stat().st_size / (1024 * 1024)  # MB
                    print(f"Загрузка: {f.name} ({size:.2f} MB)")

            time.sleep(3)

        raise TimeoutError(f"Загрузка не завершилась за {timeout} секунд")

    def wait_for_new_file(self, timeout=3600):
        """
        Ожидает появления нового файла и его полной загрузки.
        Возвращает путь к загруженному файлу.
        """
        download_path = Path(self.download_dir)
        existing_files = set(download_path.glob("*"))
        end_time = time.time() + timeout

        while time.time() < end_time:
            current_files = set(download_path.glob("*"))
            new_files = current_files - existing_files

            completed_files = [
                f for f in new_files if not f.name.endswith((".crdownload", ".tmp"))
            ]

            if completed_files:
                remaining = end_time - time.time()
                if remaining > 0:
                    self.is_download_complete(remaining)
                return completed_files[0]

            time.sleep(2)

        raise TimeoutError("Новый файл не появился в директории загрузок")

    def wait(self, sec=30):
        return WebDriverWait(self.driver, sec)

    def _find_and_click(self, css: str, *, index: int = 0, timeout: int = 10, js: bool = False) -> None:
        """Find element by CSS, log result, and click.

        Filters to visible+enabled elements only, then picks by index.

        Args:
            css: CSS selector string
            index: which visible match to use (0=first, -1=last)
            timeout: seconds to wait for at least one visible+enabled element
            js: use JavaScript click (avoids scroll/overlay interference)
        """

        idx_label = "last" if index == -1 else f"#{index}"
        print(f"[dim]>>> searching {idx_label} [{css}][/dim]")

        def visible_and_enabled(driver):
            els = [
                el
                for el in driver.find_elements(By.CSS_SELECTOR, css)
                if el.is_displayed() and el.is_enabled()
            ]
            return els if els else False

        visible = self.wait(timeout).until(
            visible_and_enabled,
            message=f"No visible+enabled element for '{css}' after {timeout}s",
        )

        print(f"[dim]    found {len(visible)} visible element(s)[/dim]")
        element = visible[index]
        tag = element.tag_name
        text = element.text.strip()[:40] or element.get_attribute("class") or ""
        print(f"[dim]    clicking <{tag}> '{text}'[/dim]")

        if js:
            self.driver.execute_script("arguments[0].click();", element)
        else:
            self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
            element.click()

        print(f"[dim]    clicked[/dim]")

    def make_backup_in_chrome(self):
        self._login()
        backups_url = f"{self.project_url}/wp-admin/admin.php?page=ai1wm_export"
        self.driver.get(backups_url)

        self._find_and_click(".ai1wm-button-export")
        time.sleep(1)
        self._find_and_click("#ai1wm-export-file")

        self._find_and_click(".ai1wm-modal-container .ai1wm-button-green", timeout=1800)

        print("Начинается загрузка бэкапа...")

        try:
            downloaded_file = self.wait_for_new_file(timeout=3600)
            print(f"Бэкап успешно загружен: {downloaded_file}")
            return downloaded_file
        except TimeoutError as e:
            print(f"Ошибка: {e}")
            raise
        finally:
            self.driver.quit()

    def waitForCaptcha(self, timeout: int = 60):
        try:
            WebDriverWait(self.driver, 1).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, ".aiowps-captcha-answer")
                )
            )
            # Captcha present — wait until it disappears (user solved it)
            WebDriverWait(self.driver, timeout).until(
                EC.invisibility_of_element_located(
                    (By.CSS_SELECTOR, ".aiowps-captcha-answer")
                )
            )
        except TimeoutException:
            return

    def _go_next_if_no_login_element(self):
        elements = self.driver.find_elements(By.ID, "user_login")
        if elements:
            print("Login element exists")
        else:
            go_next = input("Go next? [y/n]: ")
            if go_next == "y":
                print("Go next")
            else:
                exit(1)

    def restore_backup_in_chrome(self):
        self._login(check_login_element=True)
        backups_url = f"{self.project_url}/wp-admin/admin.php?page=ai1wm_backups"
        self.driver.get(backups_url)

        agree_to_delete = input("[red]Do you want to delete existing backups? [y/n]: ")
        if agree_to_delete == "y":
            self.choose_backups_to_delete()
        else:
            print("Not deleting existing backups")

        self._find_and_click("table.ai1wm-backups tr .ai1wm-backup-dots", index=0, js=True)
        time.sleep(2)
        self._find_and_click(".ai1wm-backup-restore", index=0, js=True)
        time.sleep(1)
        self._find_and_click(".ai1wm-import-modal-actions .ai1wm-button-green")

        # Wait for restore to complete — can take a long time
        self.wait(3600).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, ".ai1wm-import-modal-content-done")
            )
        )
        time.sleep(1)
        self.driver.quit()

        # Give the site time to fully come back up after restore
        time.sleep(3)

        self.driver = webdriver.Chrome(service=self.service, options=self.options)
        self._login(check_login_element=True)

        save_permalink_url = f"{self.project_url}/wp-admin/options-permalink.php"
        self.driver.get(save_permalink_url)
        submit_btn = self.wait().until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "#submit"))
        )
        self.driver.execute_script(
            "arguments[0].scrollIntoView(); arguments[0].click();", submit_btn
        )

        plugins_url = f"{self.project_url}/wp-admin/plugins.php"
        self.driver.get(plugins_url)
        self._find_and_click("#activate-wps-hide-login")

        self.driver.quit()

    def delete_backup_in_chrome(self):
        self._login()
        backups_url = f"{self.project_url}/wp-admin/admin.php?page=ai1wm_backups"
        self.driver.get(backups_url)
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
                self._find_and_click(".ai1wm-backup-delete", index=-1, js=True)

                self.wait(300).until(EC.alert_is_present())
                self.driver.switch_to.alert.accept()

                time.sleep(2)

                print(f"[green]Deleted backup {i + 1} of {num_backups}")

            except (TimeoutException, RuntimeError) as e:
                print(f"[red]Error deleting backup {i + 1}: {e}")
                raise
