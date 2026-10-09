from dataclasses import dataclass

from playwright.sync_api import Page

from classes.selenium.WPPlaywright import log
from py_libs.InputValidator import InputValidator
from py_libs.Menu import Menu


@dataclass
class WPUserRow:
    id: str
    login: str
    name: str
    email: str
    role: str
    posts: str
    delete_href: str  # empty for the current user — WP doesn't offer deleting yourself


class WPUsers:
    """Review wp-admin/users.php from the terminal (for headless runs):
    print the users table and delete the ones picked in fzf."""

    def __init__(self, page: Page, project_url: str) -> None:
        self.page = page
        self.users_url = f"{project_url}/wp-admin/users.php"

    def _cell(self, row, column: str) -> str:
        cell = row.locator(f"td.column-{column}")
        return cell.inner_text().strip() if cell.count() else ""

    def _list(self) -> list[WPUserRow]:
        users: list[WPUserRow] = []
        page_num = 1
        while True:
            self.page.goto(f"{self.users_url}?paged={page_num}")
            self.page.wait_for_load_state("load")
            for row in self.page.locator('#the-list tr[id^="user-"]').all():
                login_cell = row.locator("td.column-username strong")
                delete_link = row.locator(".row-actions .delete a")
                users.append(
                    WPUserRow(
                        id=(row.get_attribute("id") or "").removeprefix("user-"),
                        login=login_cell.inner_text().strip() if login_cell.count() else "",
                        name=self._cell(row, "name"),
                        email=self._cell(row, "email"),
                        role=self._cell(row, "role"),
                        posts=self._cell(row, "posts"),
                        delete_href=(
                            delete_link.first.get_attribute("href") or ""
                            if delete_link.count()
                            else ""
                        ),
                    )
                )
            total = self.page.locator(".tablenav.top .total-pages")
            total_pages = int(total.first.inner_text().strip()) if total.count() else 1
            if page_num >= total_pages:
                return users
            page_num += 1

    def review_in_terminal(self) -> None:
        log.info(f"Loading users from {self.users_url}")
        users = self._list()
        Menu.display(
            "Users",
            ["ID", "Login", "Name", "Email", "Role", "Posts"],
            [[u.id, u.login, u.name, u.email, u.role, u.posts] for u in users],
        )
        deletable = [u for u in users if u.delete_href]
        if not deletable:
            log.info("No users that can be deleted")
            return
        if not self._ask_delete():
            log.info("Continuing without deleting users")
            return
        lines = [f"{u.id} | {u.login} | {u.email} | {u.role}" for u in deletable]
        log.info("Pick suspicious users to delete (Esc — delete nobody)")
        picked = [deletable[i] for i in Menu.select_fzf_multi(lines)]
        if not picked:
            log.info("No users selected, continuing")
            return
        logins = ", ".join(u.login for u in picked)
        if not InputValidator.get_bool(f"[red]Delete users: {logins}? [y/n]: "):
            log.info("Users not deleted")
            return
        for user in picked:
            self._delete(user)

    @staticmethod
    def _ask_delete() -> bool:
        """'d' → pick users to delete, Enter → continue without deleting."""
        while True:
            answer = InputValidator.get_string(
                "[bold red]d[/bold red] — delete users, [bold green]Enter[/bold green] — continue: ",
                allow_empty=True,
            ).lower()
            if answer in ("", "d"):
                return answer == "d"

    def _delete(self, user: WPUserRow) -> None:
        log.info(f"Deleting user [bold]{user.login}[/bold] (ID {user.id})")
        self.page.goto(user.delete_href)
        self.page.wait_for_load_state("load")
        # a user with content gets "delete all content / attribute to" radios
        if self.page.locator("#delete_option0").count():
            reassign = self.page.locator("#reassign_user option:checked")
            reassign_to = reassign.first.inner_text().strip() if reassign.count() else "?"
            Menu.display(
                f"User {user.login} has content",
                ["Index", "Option"],
                [["0", "Delete all content"], ["1", f"Attribute to: {reassign_to}"]],
                row_styles={0: "bold red", 1: "bold blue"},
            )
            option = "#delete_option0" if Menu.choose_option() == 0 else "#delete_option1"
            self.page.check(option)
        self.page.click("#submit")
        self.page.wait_for_load_state("load")
        log.info(f"User [bold]{user.login}[/bold] deleted")
