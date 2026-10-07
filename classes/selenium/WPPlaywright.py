import logging
import os
import time
from pathlib import Path
from urllib.parse import urlparse

from playwright.sync_api import (
    sync_playwright,
    Playwright,
    Browser,
    BrowserContext,
    Page,
    TimeoutError as PlaywrightTimeoutError,
)
from rich.logging import RichHandler

from classes.projects.Project import Project

_log_path = Path(__file__).resolve().parent.parent.parent / "sessions" / "wp_playwright.log"
_log_path.parent.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.DEBUG,
    format="%(message)s",
    handlers=[
        RichHandler(rich_tracebacks=True, markup=True, show_path=False),
        logging.FileHandler(_log_path),
    ],
)
log = logging.getLogger("WPPlaywright")


SESSIONS_DIR = Path(__file__).resolve().parent.parent.parent / "sessions"


def browser_user_agent(browser: Browser) -> str:
    """A regular Chrome user agent. Headless Chromium sends "HeadlessChrome/…",
    which firewalls like NinjaFirewall answer with 403 (no login form)."""
    return (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        f"(KHTML, like Gecko) Chrome/{browser.version} Safari/537.36"
    )


def login_candidates(site_login_url: str, project_url: str) -> list[str]:
    """Urls where the login form may live, in the order they are tried
    (custom login path from list.csv first, duplicates dropped)."""
    urls = [
        site_login_url,
        f"{project_url}/wp-admin",
        f"{project_url}/gestione",
        f"{project_url}/login",
        f"{project_url}/login.php",
        f"{project_url}/wp-login.php",
    ]
    return list(dict.fromkeys(urls))
SESSIONS_DIR.mkdir(exist_ok=True)


class WPPlaywright:
    def __init__(self, theme_name: str | None = None, headless: bool = False) -> None:
        # by default the project is the current theme folder; pass a list.csv
        # title to work on another site
        theme_name = theme_name or os.path.basename(os.getcwd())
        self.pr = Project(theme_name)
        self.project = self.pr.getProject()
        self.project_url: str = self.project["url"]
        self.project_login: str = self.project["login"]
        self.project_password: str = self.project["password"]
        self.sitem_login: str = self.pr.getLoginUrl(False)
        self.session_path: str = str(SESSIONS_DIR / f"session_{theme_name}.json")
        self.download_dir: str = str(Path.home() / "Downloads")
        log.info(f"Project: [bold]{theme_name}[/bold] | URL: {self.project_url} | session: {self.session_path}")

        self.headless = headless
        self._playwright: Playwright = sync_playwright().start()
        self.browser: Browser = self._playwright.chromium.launch(headless=headless)
        self.context: BrowserContext = self._make_context()
        self.page: Page = self.context.new_page()

    def _make_context(self) -> BrowserContext:
        # some sites have no own SSL cert (server answers with the hosting's
        # cert → ERR_CERT_COMMON_NAME_INVALID); a regular browser lets you click
        # through, Playwright fails — so ignore cert errors like that click does
        if Path(self.session_path).exists():
            log.debug("Loading saved session from file")
            return self.browser.new_context(
                storage_state=self.session_path,
                accept_downloads=True,
                ignore_https_errors=True,
                user_agent=browser_user_agent(self.browser),
            )
        log.debug("No saved session, creating fresh context")
        return self.browser.new_context(
            accept_downloads=True,
            ignore_https_errors=True,
            user_agent=browser_user_agent(self.browser),
        )

    def ensure_logged_in(self) -> None:
        log.info("Navigating to wp-admin")
        self.page.goto(f"{self.project_url}/wp-admin")
        self.page.wait_for_load_state("load")
        if self._is_admin():
            log.info("Already logged in")
            self._use_actual_origin()
            return
        log.info("Not logged in, starting login flow")
        self._login()
        self._use_actual_origin()
        self._save_session()

    def relogin(self) -> str:
        """Log in again after the site dropped the session; returns the site url
        (for WPPlugins(relogin=...))."""
        self.ensure_logged_in()
        return self.project_url

    def _is_admin(self) -> bool:
        # the url alone isn't enough (a 404 under /wp-admin matches too)
        return self.page.locator("body.wp-admin").count() > 0

    def _use_actual_origin(self) -> None:
        """Switch project_url to the origin we actually ended up on in wp-admin.

        list.csv may say https://www.site.it while the site redirects to
        https://site.it (or http↔https): login cookies are set for the real
        host, so every later page must be opened there — on the other host
        we're logged out and get the login-hider's 404 instead of wp-admin.
        """
        parsed = urlparse(self.page.url)
        origin = f"{parsed.scheme}://{parsed.netloc}"
        if origin != self.project_url:
            log.warning(f"Site redirects {self.project_url} → {origin}, using {origin}")
            self.project_url = origin

    def _login(self) -> None:
        login_url = self._find_login_url()
        if login_url is None:
            raise RuntimeError("Login form not found on any candidate URL.")
        if self._is_admin():
            # the saved session was valid after all (e.g. for the non-www host)
            return

        log.info(f"Filling credentials for user: {self.project_login}")
        self.page.fill("#user_login", self.project_login)
        self.page.fill("#user_pass", self.project_password)
        self.page.click("#wp-submit")
        log.debug("Waiting for redirect to wp-admin after login")
        self.page.wait_for_url(
            lambda url: "/wp-admin" in url and "wp-login" not in url,
            timeout=30_000,
        )
        log.info("Login successful")

    def _find_login_url(self) -> str | None:
        for url in login_candidates(self.sitem_login, self.project_url):
            log.debug(f"Trying login URL: {url}")
            for attempt in range(10):
                try:
                    self.page.goto(url)
                    break
                except Exception as e:
                    if attempt == 9:
                        raise
                    log.warning(
                        f"Server not ready, retrying in 5s... ({attempt + 1}/10): "
                        f"{str(e).splitlines()[0]}"
                    )
                    time.sleep(5)
            self._wait_for_captcha()
            log.debug(f"  actual URL after navigation: {self.page.url}")
            # the login page may redirect straight into wp-admin when the
            # session is valid on the real host — nothing to fill in then
            if self._is_admin():
                log.info(f"Already logged in (redirected to {self.page.url})")
                return url
            if self.page.locator("#user_login").count() > 0:
                log.info(f"Login form found at: {url}")
                return url
            log.debug(f"No login form at: {url} (ended up at {self.page.url})")
        return None

    def _wait_for_captcha(self, timeout: int = 60):
        try:
            self.page.wait_for_selector(
                ".aiowps-captcha-answer", state="visible", timeout=1_000
            )
            log.warning(
                f"Captcha detected, waiting up to {timeout}s for it to be solved"
            )
            self.page.wait_for_selector(
                ".aiowps-captcha-answer", state="hidden", timeout=timeout * 1_000
            )
            log.info("Captcha resolved")
        except PlaywrightTimeoutError:
            return

    def goToUsers(self) -> None:
        users_url = f"{self.project_url}/wp-admin/users.php"
        log.info(f"Navigating to users page: {users_url}")
        if self.headless:
            from classes.selenium.WPUsers import WPUsers

            WPUsers(self.page, self.project_url).review_in_terminal()
            return
        self.page.goto(users_url)
        self.page.wait_for_load_state("load")
        input("Проверьте страницу пользователей, удалите подозрительных, затем нажмите Enter для продолжения...")

    def _save_session(self) -> None:
        self.context.storage_state(path=self.session_path)
        log.info(f"Session saved → {self.session_path}")

    def close(self) -> None:
        log.info("Closing browser and saving session")
        self._save_session()
        self.browser.close()
        self._playwright.stop()
        log.debug("Browser closed")

    # ── shared helpers ────────────────────────────────────────────────────────

    def _find_and_click(
        self, css: str, *, index: int = 0, timeout: int = 10, js: bool = False
    ) -> None:
        idx_label = "last" if index == -1 else f"#{index}"
        log.debug(f"Searching {idx_label} [{css}]")

        locator = self.page.locator(css)
        locator.first.wait_for(state="visible", timeout=timeout * 1_000)

        count = locator.count()
        log.debug(f"Found {count} element(s) for [{css}]")

        element = locator.last if index == -1 else locator.nth(index)
        tag = element.evaluate("el => el.tagName.toLowerCase()")
        text = (
            (element.inner_text() or "").strip()[:40]
            or element.get_attribute("class")
            or ""
        )
        log.debug(f"Clicking <{tag}> '{text}' (js={js})")

        if js:
            element.dispatch_event("click")
        else:
            element.click(timeout=30_000)
        log.debug(f"Clicked [{css}]")

    def _get_visible_link_target(
        self, css: str, *, index: int = 0, timeout: int = 10
    ) -> tuple[str, str]:
        from urllib.parse import urlparse

        idx_label = "last" if index == -1 else f"#{index}"
        log.debug(f"Resolving link {idx_label} [{css}]")

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
        log.debug(f"Link href: {href} | filename: {filename}")
        return href, filename

    def _download_from_link(
        self, css: str, *, index: int = 0, timeout: int = 10
    ) -> Path:
        href, fallback_filename = self._get_visible_link_target(
            css, index=index, timeout=timeout
        )
        log.info(f"Starting download from: {href}")

        with self.page.expect_download(timeout=3_600_000) as download_info:
            self.page.evaluate("url => window.location.assign(url)", href)

        download = download_info.value

        # chrome://downloads only shows progress in the window — no use headless
        downloads_page = None if self.headless else self.context.new_page()
        if downloads_page:
            downloads_page.goto("chrome://downloads/")

        suggested_filename = download.suggested_filename or fallback_filename
        save_path = Path(self.download_dir) / suggested_filename
        download.save_as(str(save_path))
        if downloads_page:
            downloads_page.close()
        log.info(f"Downloaded → {save_path}")
        return save_path
