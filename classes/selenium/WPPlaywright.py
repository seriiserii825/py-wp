import os
import time
from pathlib import Path

from playwright.sync_api import sync_playwright, Playwright, Browser, BrowserContext, Page, TimeoutError as PlaywrightTimeoutError
from rich import print

from classes.projects.Project import Project


SESSIONS_DIR = Path(__file__).resolve().parent.parent.parent / "sessions"
SESSIONS_DIR.mkdir(exist_ok=True)


class WPPlaywright:
    def __init__(self) -> None:
        theme_name = os.path.basename(os.getcwd())
        self.pr = Project(theme_name)
        self.project = self.pr.getProject()
        self.project_url: str = self.project["url"]
        self.project_login: str = self.project["login"]
        self.project_password: str = self.project["password"]
        self.sitem_login: str = self.pr.getLoginUrl(False)
        self.session_path: str = str(SESSIONS_DIR / f"session_{theme_name}.json")
        self.download_dir: str = str(Path.home() / "Downloads")

        self._playwright: Playwright = sync_playwright().start()
        self.browser: Browser = self._playwright.chromium.launch(headless=False)
        self.context: BrowserContext = self._make_context()
        self.page: Page = self.context.new_page()

    def _make_context(self) -> BrowserContext:
        if Path(self.session_path).exists():
            return self.browser.new_context(
                storage_state=self.session_path, accept_downloads=True
            )
        return self.browser.new_context(accept_downloads=True)

    def ensure_logged_in(self) -> None:
        self.page.goto(f"{self.project_url}/wp-admin")
        self.page.wait_for_load_state("networkidle")
        if "/wp-admin" in self.page.url and "wp-login" not in self.page.url:
            return
        self._login()
        self._save_session()

    def _login(self) -> None:
        login_url = self._find_login_url()
        if login_url is None:
            raise RuntimeError("Login form not found on any candidate URL.")

        self.page.fill("#user_login", self.project_login)
        self.page.fill("#user_pass", self.project_password)
        self.page.click("#wp-submit")
        self.page.wait_for_url(
            lambda url: "/wp-admin" in url and "wp-login" not in url,
            timeout=30_000,
        )

    def _find_login_url(self) -> str | None:
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
                    print(f"[dim]server not ready, retrying in 5s... ({attempt + 1}/10)[/dim]")
                    time.sleep(5)
            self._wait_for_captcha()
            if self.page.locator("#user_login").count() > 0:
                return url
        return None

    def _wait_for_captcha(self, timeout: int = 60):
        try:
            self.page.wait_for_selector(".aiowps-captcha-answer", state="visible", timeout=1_000)
            self.page.wait_for_selector(".aiowps-captcha-answer", state="hidden", timeout=timeout * 1_000)
        except PlaywrightTimeoutError:
            return

    def _save_session(self) -> None:
        self.context.storage_state(path=self.session_path)
        print(f"[green]Session saved → {self.session_path}")

    def close(self) -> None:
        self._save_session()
        self.browser.close()
        self._playwright.stop()

    # ── shared helpers ────────────────────────────────────────────────────────

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
        from urllib.parse import urlparse
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

    def _download_from_link(self, css: str, *, index: int = 0, timeout: int = 10) -> Path:
        href, fallback_filename = self._get_visible_link_target(css, index=index, timeout=timeout)

        with self.page.expect_download(timeout=3_600_000) as download_info:
            self.page.evaluate("url => window.location.assign(url)", href)

        download = download_info.value

        downloads_page = self.context.new_page()
        downloads_page.goto("chrome://downloads/")

        suggested_filename = download.suggested_filename or fallback_filename
        save_path = Path(self.download_dir) / suggested_filename
        download.save_as(str(save_path))
        downloads_page.close()
        print(f"[green]Downloaded → {save_path}")
        return save_path
