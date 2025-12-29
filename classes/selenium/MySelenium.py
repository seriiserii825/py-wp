import os
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


class MySelenium:
    def __init__(self):
        self.service = Service(executable_path="/usr/bin/chromedriver")
        self.download_dir = str(Path.home() / "Downloads")
        self.options = webdriver.ChromeOptions()
        self.options.add_argument(
            "user-data-dir=/home/serii/.config/google-chrome/My-profile"
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

    def every_downloads_chrome(self, driver):
        if not driver.current_url.startswith("chrome://downloads"):
            driver.get("chrome://downloads/")
        return driver.execute_script("""
            const items = document.querySelector('downloads-manager')
                .shadowRoot.getElementById('downloadsList').items;
            if (items.every(e => e.state === "COMPLETE"))
                return items.map(e => e.fileUrl || e.file_url);
        """)

    def loginToSite(self):
        while True:
            req = requests.get(self.sitem_login)
            if req.status_code != requests.codes["ok"]:
                self.sitem_login = f"{self.project_url}/wp-admin"
                break
            else:
                break

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
            # Ищем временные файлы загрузки Chrome
            temp_files = list(download_path.glob("*.crdownload"))
            tmp_files = list(download_path.glob("*.tmp"))

            if not temp_files and not tmp_files:
                # Даём файлу время на финализацию
                time.sleep(2)
                return True

            # Выводим прогресс (опционально)
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

        # Запоминаем существующие файлы
        existing_files = set(download_path.glob("*"))

        end_time = time.time() + timeout

        # Ждём появления нового файла
        while time.time() < end_time:
            current_files = set(download_path.glob("*"))
            new_files = current_files - existing_files

            # Исключаем временные файлы
            completed_files = [
                f for f in new_files if not f.name.endswith((".crdownload", ".tmp"))
            ]

            if completed_files:
                # Ждём завершения загрузки
                self.is_download_complete(
                    timeout - (time.time() - (end_time - timeout))
                )
                return completed_files[0]

            time.sleep(2)

        raise TimeoutError("Новый файл не появился в директории загрузок")

    def wait(self, sec=30):
        return WebDriverWait(self.driver, sec)

    def make_backup_in_chrome(self):
        self.loginToSite()
        self.driver.get(self.sitem_login)
        self.waitForCaptcha()
        login_element = self.driver.find_element(By.ID, "user_login")
        login_element.send_keys(self.project_login)
        password_element = self.driver.find_element(By.ID, "user_pass")
        password_element.send_keys(self.project_password)
        login_button = self.driver.find_element(By.ID, "wp-submit")
        login_button.click()
        backups_url = f"{self.project_url}/wp-admin/admin.php?page=ai1wm_export"
        self.driver.get(backups_url)

        if self.driver.current_url != backups_url:
            self.driver.get(backups_url)

        dots_btn = self.wait().until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".ai1wm-button-export"))
        )
        dots_btn.click()

        export_btn = self.wait().until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "#ai1wm-export-file"))
        )

        time.sleep(1)

        export_btn.click()

        btn_green = self.wait().until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, ".ai1wm-modal-container .ai1wm-button-green")
            )
        )

        btn_green.click()

        print("Начинается загрузка бэкапа...")

        try:
            # Ожидаем завершения загрузки (максимум 1 час)
            downloaded_file = self.wait_for_new_file(timeout=3600)
            print(f"Бэкап успешно загружен: {downloaded_file}")
            return downloaded_file
        except TimeoutError as e:
            print(f"Ошибка: {e}")
            raise
        finally:
            self.driver.quit()

        # WebDriverWait(self.driver, 120, 1).until(self.every_downloads_chrome)
        # self.driver.close()
        # time.sleep(10000000)

    def waitForCaptcha(self):
        try:
            WebDriverWait(self.driver, 1).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, ".aiowps-captcha-answer")
                )
            )
            aiowps_captcha_answer = self.driver.find_element(
                By.CSS_SELECTOR, ".aiowps-captcha-answer"
            )
            if aiowps_captcha_answer:
                time.sleep(10)
        except TimeoutException:
            return

    def _go_next_if_no_login_element(self):
        elements = self.driver.find_elements(By.ID, "user_login")
        if elements:  # list is not empty
            print("Login element exists")
        else:
            go_next = input("Go next? [y/n]: ")
            if go_next == "y":
                print("Go next")
            else:
                exit(1)

    def restore_backup_in_chrome(self):
        self.loginToSite()
        self.driver.get(self.sitem_login)
        self.waitForCaptcha()
        self._go_next_if_no_login_element()
        login_element = self.driver.find_element(By.ID, "user_login")
        login_element.send_keys(self.project_login)
        password_element = self.driver.find_element(By.ID, "user_pass")
        password_element.send_keys(self.project_password)
        login_button = self.driver.find_element(By.ID, "wp-submit")
        login_button.click()
        backups_url = f"{self.project_url}/wp-admin/admin.php?page=ai1wm_backups"
        self.driver.get(backups_url)

        # check current url is backups_url
        if self.driver.current_url != backups_url:
            self.driver.get(backups_url)

        agree_to_delete = input("[red]Do you want to delete existing backups? [y/n]: ")
        if agree_to_delete == "y":
            self.choose_backups_to_delete()
        else:
            print("Not deleting existing backups")

        WebDriverWait(self.driver, 3000).until(
            EC.presence_of_element_located(
                (
                    By.CSS_SELECTOR,
                    "table.ai1wm-backups tr:nth-of-type(2) .ai1wm-backup-dots",
                )
            )
        )
        ai1wm_backup_dots = self.driver.find_element(
            By.CSS_SELECTOR, "table.ai1wm-backups tr:nth-of-type(2) .ai1wm-backup-dots"
        )
        ai1wm_backup_dots.click()
        WebDriverWait(self.driver, 3000).until(
            EC.presence_of_element_located(
                (
                    By.CSS_SELECTOR,
                    "table.ai1wm-backups tr:nth-of-type(2) .ai1wm-backup-restore",
                )
            )
        )
        ai1wm_backup_restore = self.driver.find_element(
            By.CSS_SELECTOR,
            "table.ai1wm-backups tr:nth-of-type(2) .ai1wm-backup-restore",
        )
        ai1wm_backup_restore.click()
        WebDriverWait(self.driver, 3000).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, ".ai1wm-import-modal-actions .ai1wm-button-green")
            )
        )
        button_green = self.driver.find_element(
            By.CSS_SELECTOR, ".ai1wm-import-modal-actions .ai1wm-button-green"
        )
        button_green.click()
        WebDriverWait(self.driver, 3000).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, ".ai1wm-import-modal-content-done")
            )
        )
        time.sleep(1)
        self.driver.close()
        self.driver = webdriver.Chrome(service=self.service, options=self.options)
        self.loginToSite()
        self.driver.get(self.sitem_login)
        self.waitForCaptcha()
        self._go_next_if_no_login_element()
        login_element = self.driver.find_element(By.ID, "user_login")
        login_element.send_keys(self.project_login)
        password_element = self.driver.find_element(By.ID, "user_pass")
        password_element.send_keys(self.project_password)
        login_button = self.driver.find_element(By.ID, "wp-submit")
        login_button.click()
        save_permalink_url = f"{self.project_url}/wp-admin/options-permalink.php"
        self.driver.get(save_permalink_url)
        WebDriverWait(self.driver, 3000).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#submit"))
        )
        submit_button = self.driver.find_element(By.CSS_SELECTOR, "#submit")
        submit_button.click()
        plugins_url = f"{self.project_url}/wp-admin/plugins.php"
        self.driver.get(plugins_url)
        # if current_url is not plugins_url, then go to plugins_url
        if self.driver.current_url != plugins_url:
            self.driver.get(plugins_url)
        WebDriverWait(self.driver, 3000).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "#activate-wps-hide-login")
            )
        )
        wps_hide_login = self.driver.find_element(
            By.CSS_SELECTOR, "#activate-wps-hide-login"
        )
        wps_hide_login.click()
        self.driver.close()

    def delete_backup_in_chrome(self):
        self.loginToSite()
        self.driver.get(self.sitem_login)
        self.waitForCaptcha()
        login_element = self.driver.find_element(By.ID, "user_login")
        login_element.send_keys(self.project_login)
        password_element = self.driver.find_element(By.ID, "user_pass")
        password_element.send_keys(self.project_password)
        login_button = self.driver.find_element(By.ID, "wp-submit")
        login_button.click()
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
                # Wait for backup table to be ready
                self.wait(300).until(
                    EC.presence_of_element_located(
                        (
                            By.CSS_SELECTOR,
                            "table.ai1wm-backups tr:last-of-type .ai1wm-backup-dots",
                        )
                    )
                )

                # Always delete the last backup (most recent) - after deletion, next one becomes last
                dots_button = self.wait(300).until(
                    EC.element_to_be_clickable(
                        (
                            By.CSS_SELECTOR,
                            "table.ai1wm-backups tr:last-of-type .ai1wm-backup-dots",
                        )
                    )
                )
                dots_button.click()

                # Wait for delete button and click it
                delete_button = self.wait(300).until(
                    EC.element_to_be_clickable(
                        (
                            By.CSS_SELECTOR,
                            "table.ai1wm-backups tr:last-of-type .ai1wm-backup-delete",
                        )
                    )
                )
                delete_button.click()

                # Handle confirmation alert
                self.wait(300).until(EC.alert_is_present())
                self.driver.switch_to.alert.accept()

                # Wait for deletion to complete
                time.sleep(2)

                print(f"[green]Deleted backup {i + 1} of {num_backups}")

            except TimeoutException as e:
                print(f"[red]Timeout error deleting backup {i + 1}: {str(e)}")
                raise
            except Exception as e:
                print(f"[red]Error deleting backup {i + 1}: {str(e)}")
                raise
