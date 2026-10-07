import re
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Callable, Iterable, Iterator

from playwright.sync_api import Error as PlaywrightError, Page

from classes.selenium.WPPlaywright import log
from py_libs.Notification import Notification


BACKUP_PLUGINS = [
    "all-in-one-wp-migration",
    "all-in-one-wp-migration-unlimited-extension",
]
# not installed on every site — skipped with a warning instead of aborting
BACKUP_PLUGINS_OPTIONAL = ["all-in-one-wp-migration-unlimited-extension"]


class PluginNotInstalledError(RuntimeError):
    pass


class WPPlugins:
    """Activate/deactivate plugins on wp-admin/plugins.php by their slug.

    WordPress renders `#activate-<slug>` for inactive plugins and
    `#deactivate-<slug>` for active ones, so the link id tells us the state.
    """

    def __init__(
        self,
        page: Page,
        project_url: str,
        relogin: Callable[[], str] | None = None,
    ) -> None:
        """`relogin` logs in again and returns the (possibly changed) site url;
        used when the site drops the session mid-run (seen right after a
        plugin deactivation, likely a security plugin on the site)."""
        self.page = page
        self.relogin = relogin
        self._set_url(project_url)

    def _set_url(self, project_url: str) -> None:
        self.plugins_url = f"{project_url}/wp-admin/plugins.php"

    def _is_plugins_page(self) -> bool:
        return self.page.locator("body.plugins-php").count() > 0

    def _log_where(self, after: str) -> None:
        """Diagnostics: where the browser ended up after an action."""
        logged_in = self.page.locator("body.wp-admin").count() > 0
        log.debug(f"  after {after}: {self.page.url} (logged in: {logged_in})")
        if self.plugins_url.startswith("https://") and self.page.url.startswith("http://"):
            # WP redirects after admin actions to its own address; https login
            # cookies aren't sent over http → looks logged out (hide-login 404)
            log.warning(
                "WordPress redirected to http:// — the site's address in "
                "Settings → General is http, should be https. Continuing over https."
            )

    def _open(self) -> None:
        # without the check a 404 / login page would look like "plugin not installed"
        self._goto_admin_page("plugins.php", "body.plugins-php")

    def _goto_admin_page(self, path: str, body_selector: str) -> None:
        """Open wp-admin/<path> and make sure it really is that page; if the site
        dropped the session, log in again once (when `relogin` is given)."""
        self._goto(self.plugins_url.replace("plugins.php", path))
        if self.page.locator(body_selector).count() > 0:
            return
        if self.relogin is None:
            raise RuntimeError(
                f"{path} didn't open (ended up at {self.page.url}) — not logged in?"
            )
        log.warning(f"Session lost (ended up at {self.page.url}), logging in again")
        self._set_url(self.relogin())
        self._goto(self.plugins_url.replace("plugins.php", path))
        if self.page.locator(body_selector).count() == 0:
            raise RuntimeError(
                f"{path} didn't open even after re-login (ended up at {self.page.url})"
            )

    def _goto(self, url: str, attempts: int = 3) -> None:
        """goto() that survives net::ERR_ABORTED — seen right after an action
        redirected to http:// and the next https navigation collided with it."""
        for attempt in range(1, attempts + 1):
            try:
                self.page.goto(url)
                self.page.wait_for_load_state("load")
                return
            except PlaywrightError as e:
                if "ERR_ABORTED" not in str(e) or attempt == attempts:
                    raise
                log.warning(f"Navigation to {url} aborted, retrying ({attempt}/{attempts})")
                time.sleep(2)

    def _has(self, link_id: str) -> bool:
        return self.page.locator(f"#{link_id}").count() > 0

    def _toggle(self, slugs: list[str], action: str, optional: Iterable[str] = ()) -> list[str]:
        """Click `#<action>-<slug>` for every slug not yet in the target state.

        A slug missing from the plugins page (not installed) raises
        PluginNotInstalledError on activate, unless it is listed in `optional`.
        On deactivate a missing plugin is never an error — there's nothing to turn off.
        """
        opposite = "deactivate" if action == "activate" else "activate"
        changed: list[str] = []

        for slug in slugs:
            self._open()
            if self._has(f"{action}-{slug}"):
                log.info(f"Plugin [bold]{slug}[/bold]: {action} → clicking")
                self.page.click(f"#{action}-{slug}")
                self.page.wait_for_load_state("load")
                self._log_where(f"{action} {slug}")
                changed.append(slug)
            elif self._has(f"{opposite}-{slug}"):
                log.info(f"Plugin [bold]{slug}[/bold]: already {action}d, skipping")
            elif action == "activate" and slug not in optional:
                log.error(f"Required plugin [bold]{slug}[/bold] is not installed")
                Notification(
                    title="Required plugin not installed",
                    message=slug,
                ).notify()
                raise PluginNotInstalledError(
                    f"Required plugin '{slug}' not found on {self.plugins_url} — install it first"
                )
            else:
                log.warning(f"Plugin [bold]{slug}[/bold] not found on plugins page, skipping")

        if changed:
            Notification(
                title=f"Plugins {action}d",
                message="\n".join(changed),
            ).notify()
        return changed

    def activate(self, slugs: list[str], optional: Iterable[str] = ()) -> list[str]:
        return self._toggle(slugs, "activate", optional)

    def deactivate(self, slugs: list[str]) -> list[str]:
        return self._toggle(slugs, "deactivate")

    def delete(self, slug: str) -> bool:
        """Deactivate (if active) and delete a plugin via `#delete-<slug>`.

        Returns False if the plugin is not installed — nothing to delete.
        """
        self.deactivate([slug])
        self._open()
        if not self._has(f"delete-{slug}"):
            log.warning(f"Plugin [bold]{slug}[/bold] not installed, skipping delete")
            return False
        log.info(f"Plugin [bold]{slug}[/bold]: delete → clicking")
        # WP asks "Are you sure you want to delete...?" via confirm()
        self.page.once("dialog", lambda dialog: dialog.accept())
        self.page.click(f"#delete-{slug}")
        # deletion is ajax: the delete link disappears once the plugin is gone
        self.page.locator(f"#delete-{slug}").wait_for(state="detached", timeout=60_000)
        self._log_where(f"delete {slug}")
        log.info(f"Plugin [bold]{slug}[/bold] deleted")
        Notification(title="Plugin deleted", message=slug).notify()
        return True

    def installed_version(self, slug: str) -> str | None:
        """Version shown in the plugin's row on plugins.php ("Versione 1.1.0 | Di …"),
        None if the plugin isn't installed or the version can't be read."""
        self._open()
        row = self.page.locator(f'tr[data-slug="{slug}"] .plugin-version-author-uri')
        if row.count() == 0:
            return None
        match = re.search(r"\d+(?:\.\d+)+", row.first.inner_text())
        return match.group(0) if match else None

    def is_installed(self, slug: str) -> bool:
        self._open()
        return self._has(f"activate-{slug}") or self._has(f"deactivate-{slug}")

    def install_from_wordpress_org(self, slug: str) -> None:
        """Add plugin → search the slug → "Install now" (ajax); doesn't activate.
        For plugins listed as `<slug>,False` in base-plugins.csv (no local zip)."""
        log.info(f"Installing [bold]{slug}[/bold] from wordpress.org")
        self._goto_admin_page(
            f"plugin-install.php?s={slug}&tab=search&type=term", "body.plugin-install-php"
        )
        install = self.page.locator(f'a.install-now[data-slug="{slug}"]')
        try:
            install.first.wait_for(state="visible", timeout=30_000)
        except PlaywrightError:
            Notification(title="Plugin NOT installed", message=slug).notify()
            raise RuntimeError(
                f"No 'Install now' for {slug} on {self.page.url} — plugin installs "
                "blocked on this site, or the plugin isn't found on wordpress.org?"
            )
        install.first.click()
        # when the ajax install finishes the button turns into "Activate"
        self.page.locator(f'a.activate-now[data-slug="{slug}"]').first.wait_for(
            state="visible", timeout=120_000
        )
        self._log_where(f"install {slug}")
        log.info(f"Plugin [bold]{slug}[/bold] installed")
        Notification(title="Plugin installed", message=slug).notify()

    def can_upload(self) -> bool:
        """True if Add plugin → Upload plugin is available. Security plugins
        (e.g. NinjaFirewall) or DISALLOW_FILE_MODS remove the upload form."""
        self._goto_admin_page("plugin-install.php?tab=upload", "body.plugin-install-php")
        return self.page.locator("#pluginzip").count() > 0

    def upload(self, zip_path: Path) -> None:
        """Install a plugin from a local zip via Add plugin → Upload plugin."""
        if not zip_path.exists():
            raise FileNotFoundError(f"Plugin zip not found: {zip_path}")
        log.info("Opening Add plugin → Upload plugin")
        # ?tab=upload shows the upload form right away — no toggle click needed
        if not self.can_upload():
            raise RuntimeError(
                f"No upload form on {self.page.url} — plugin installs disabled on this site?"
            )
        # fills the file input directly — no OS file dialog needed
        self.page.set_input_files("#pluginzip", str(zip_path))
        log.info(f"Uploading [bold]{zip_path.name}[/bold]")
        self.page.click("#install-plugin-submit")
        self.page.wait_for_load_state("load", timeout=120_000)
        self._log_where(f"upload {zip_path.name}")
        # the result page offers "Activate plugin" only when install succeeded
        if self.page.locator('a[href*="action=activate"]').count() == 0:
            Notification(title="Plugin NOT installed", message=zip_path.name).notify()
            raise RuntimeError(f"Plugin upload failed: {zip_path.name} (see {self.page.url})")
        log.info(f"Plugin [bold]{zip_path.name}[/bold] installed")
        Notification(title="Plugin installed", message=zip_path.name).notify()

    def activate_after_upload(self) -> None:
        """Click "Activate plugin" on the page shown right after upload()."""
        log.info("Activating uploaded plugin")
        self.page.click('a[href*="action=activate"]')
        self.page.wait_for_load_state("load")
        self._log_where("activate uploaded plugin")

    @contextmanager
    def activated(self, slugs: list[str], optional: Iterable[str] = ()) -> Iterator[None]:
        """Activate plugins for the duration of the block, deactivate them afterwards.

        Deactivation runs in reverse order (extension before its base plugin) and
        even if activation or the block raised; its own errors are logged, not
        re-raised, so they don't mask the original exception.
        """
        try:
            self.activate(slugs, optional)
            yield
        finally:
            try:
                self.deactivate(list(reversed(slugs)))
            except Exception as e:
                log.error(f"Failed to deactivate plugins {slugs}: {e}")
                Notification(
                    title="Plugins NOT deactivated",
                    message="\n".join(slugs),
                ).notify()
