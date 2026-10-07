from contextlib import contextmanager
from pathlib import Path
from typing import Iterable, Iterator

from playwright.sync_api import Page

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

    def __init__(self, page: Page, project_url: str) -> None:
        self.page = page
        self.plugins_url = f"{project_url}/wp-admin/plugins.php"

    def _open(self) -> None:
        self.page.goto(self.plugins_url)
        self.page.wait_for_load_state("load")

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
        log.info(f"Plugin [bold]{slug}[/bold] deleted")
        Notification(title="Plugin deleted", message=slug).notify()
        return True

    def upload(self, zip_path: Path) -> None:
        """Install a plugin from a local zip via Add plugin → Upload plugin."""
        if not zip_path.exists():
            raise FileNotFoundError(f"Plugin zip not found: {zip_path}")
        install_url = self.plugins_url.replace("plugins.php", "plugin-install.php")
        log.info(f"Navigating to {install_url}")
        self.page.goto(install_url)
        self.page.wait_for_load_state("load")
        self.page.click(".upload-view-toggle")
        # fills the file input directly — no OS file dialog needed
        self.page.set_input_files("#pluginzip", str(zip_path))
        log.info(f"Uploading [bold]{zip_path.name}[/bold]")
        self.page.click("#install-plugin-submit")
        self.page.wait_for_load_state("load", timeout=120_000)
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
