from playwright.sync_api import Page

from classes.selenium.WPPlaywright import log
from py_libs.InputValidator import InputValidator
from py_libs.Menu import Menu

ROWS = "table.ai1wm-backups tbody tr"


class AI1WMBackups:
    """Pick All-in-One WP Migration backups to delete from the terminal
    (for headless runs) instead of looking at the backups page."""

    def __init__(self, page: Page, project_url: str) -> None:
        self.page = page
        self.backups_url = f"{project_url}/wp-admin/admin.php?page=ai1wm_backups"

    def _list(self) -> list[list[str]]:
        """Each backup as its visible cells: [filename, date, size, ...]."""
        self.page.goto(self.backups_url)
        self.page.wait_for_load_state("load")
        backups: list[list[str]] = []
        for row in self.page.locator(ROWS).all():
            cells = [c.strip() for c in row.locator("td").all_inner_texts()]
            cells = [c for c in cells if c]
            if not cells:
                continue
            # the name cell can hold a label line too — keep the .wpress line
            name_lines = [ln.strip() for ln in cells[0].splitlines() if ln.strip()]
            cells[0] = next(
                (ln for ln in name_lines if ln.endswith(".wpress")), name_lines[0]
            )
            backups.append(cells)
        return backups

    def show(self) -> list[list[str]]:
        """Print the backups table, return the backups (newest first, as on the page)."""
        backups = self._list()
        if not backups:
            log.info("No backups on server")
            return backups
        width = max(len(b) for b in backups)
        columns = ["Index", "Backup"] + [""] * (width - 1)
        Menu.display(
            "Backups on server",
            columns,
            [[str(i)] + b + [""] * (width - len(b)) for i, b in enumerate(backups)],
        )
        return backups

    def choose_and_delete(self, backups: list[list[str]] | None = None) -> None:
        """Pass `backups` from show() to skip printing the table again."""
        if backups is None:
            backups = self.show()
        if not backups:
            return
        lines = [" | ".join(b) for b in backups]
        log.info("Pick backups to delete (Esc — delete nothing)")
        picked = [backups[i][0] for i in Menu.select_fzf_multi(lines)]
        if not picked:
            log.info("No backups selected")
            return
        if not InputValidator.get_bool(f"[red]Delete {len(picked)} backup(s)? [y/n]: "):
            log.info("Backups not deleted")
            return
        for filename in picked:
            self._delete(filename)

    def _delete(self, filename: str) -> None:
        log.info(f"Deleting backup [bold]{filename}[/bold]")
        row = self.page.locator(ROWS).filter(has_text=filename)
        row.locator(".ai1wm-backup-dots").first.dispatch_event("click")
        menu_delete = self.page.locator(
            '.ai1wm-backup-dots-menu[style*="block"] .ai1wm-backup-delete'
        )
        menu_delete.first.wait_for(state="visible", timeout=10_000)
        self.page.once("dialog", lambda dialog: dialog.accept())
        menu_delete.first.dispatch_event("click")
        row.first.wait_for(state="detached", timeout=60_000)
        log.info(f"Backup [bold]{filename}[/bold] deleted")
