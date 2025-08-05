from typing_extensions import List
from classes.utils.Command import Command
from classes.utils.Menu import Menu
from classes.utils.Print import Print
from classes.utils.Select import Select
from classes.utils.WPPaths import WPPaths
from dto.PageDto import PageDto


class Page:
    pages: List[PageDto] = []

    @classmethod
    def list_pages(cls):
        pages = cls.get_page_list()
        headers = ["ID", "Title", "Status", "Date"]
        data = [
            [str(page.ID), page.post_title, page.post_status, page.post_date]
            for page in pages
        ]
        # sort by date
        data.sort(key=lambda x: x[3], reverse=False)
        Menu.display(
            "List of Pages",
            headers,
            data,
        )

    @staticmethod
    def get_page_list() -> List[PageDto]:  # noqa: F821
        data = Command.run_json("wp post list --post_type=page --format=json")
        return [PageDto(**item) for item in data]

    @classmethod
    def _get_pages_ids(cls) -> List[int]:
        if not cls.pages:
            cls.pages = cls.get_page_list()
        return [page.ID for page in cls.pages]

    @classmethod
    def get_page_by_id(cls, page_id: int) -> PageDto:
        if not cls.pages:
            cls.pages = cls.get_page_list()
        for page in cls.pages:
            if page.ID == page_id:
                return page
        raise ValueError(f"Page with ID {page_id} not found.")

    @staticmethod
    def create_one():
        title = input("Enter the title: ")
        command = (
            f"wp post create --post_type=page --post_status=publish "
            f"--post_title='{title}'"
        )
        Command.run(command)

    @staticmethod
    def create_multiple():
        titles = input("Enter the titles separated by commas: ")
        print(titles)
        titles = titles.split(",")
        for title in titles:
            title = title.strip()
            command = (
                f"wp post create --post_type=page "
                f"--post_status=publish --post_title='{title}'"
            )
            Command.run(command)

    @classmethod
    def delete_one(cls):
        pages_id = cls._select_page()
        page_id = pages_id[0]
        Command.run(f"wp post delete {page_id} --force")
        print(f"Page with ID {page_id} deleted successfully.")

    @classmethod
    def delete_multiple(cls):
        pages_id = cls._select_page()
        for page_id in pages_id:
            Command.run(f"wp post delete {page_id} --force")
            print(f"Page with ID {page_id} deleted successfully.")

    @classmethod
    def _select_page(cls) -> list[int]:
        pages = cls.get_page_list()
        pages_to_list = [f"{page.ID}-{page.post_title}" for page in pages]
        selected_pages = Select.select_with_fzf(pages_to_list)
        pages_id = [
            int(selected_page.split("-")[0]) for selected_page in selected_pages
        ]
        return pages_id

    @classmethod
    def _select_unignored_pages(cls) -> list[int]:
        ignored_pages = cls._get_ignored_pages_ids()
        all_pages_id = cls._get_pages_ids()
        unignored_pages_id = list(set(all_pages_id) - set(ignored_pages))
        if not unignored_pages_id:
            Print.error("No pages to ignore.")
            return []

        pages = [cls.get_page_by_id(page_id) for page_id in unignored_pages_id]
        pages_to_ignore = [f"{page.ID}-{page.post_title}" for page in pages]

        selected_pages = Select.select_multiple(pages_to_ignore)
        if not selected_pages:
            return []

        pages_id = [
            int(selected_page.split("-")[0]) for selected_page in selected_pages
        ]
        return pages_id

    @classmethod
    def ignore(cls):
        cls.list_pages()
        cls.list_ignored_pages()
        func_php_file_path = cls._get_func_file_path()

        with open(func_php_file_path, "r") as read_file:
            lines = read_file.readlines()

        pages_id = cls._select_unignored_pages()
        if not pages_id:
            Print.error("No pages selected to ignore.")
            return

        page_id = pages_id[0]
        updated_lines = []

        for line in lines:
            if "$ids" in line:
                line = line.replace("];", f",{page_id}];")
            updated_lines.append(line)

        with open(func_php_file_path, "w") as file:
            file.writelines(updated_lines)

        print(f"Updated {func_php_file_path} with new page ID to ignore.")

    @classmethod
    def _get_ignored_pages_ids(cls) -> List[int]:
        func_php_file_path = cls._get_func_file_path()
        with open(func_php_file_path, "r") as file:
            lines = file.readlines()
            for line in lines:
                if "$ids" in line:
                    # $ids = [8,2,680,690,40,34];
                    ids_str = line.split("=")[1].strip().rstrip(";")
                    ids_str = ids_str.strip("[]")
                    ids = ids_str.split(",")
                    return [int(id.strip()) for id in ids if id.strip().isdigit()]
        return []

    @classmethod
    def list_ignored_pages(cls):
        ignored_pages = cls._get_ignored_pages_ids()
        if not ignored_pages:
            Print.info("No ignored pages found.")
            return
        pages: List[PageDto] = []
        for page_id in ignored_pages:
            try:
                page = cls.get_page_by_id(page_id)
                pages.append(page)
            except ValueError:
                Print.error(f"Page with ID {page_id} not found.")
        headers = ["ID", "Title", "Status", "Date"]
        data = [
            [str(page.ID), page.post_title, page.post_status, page.post_date]
            for page in pages
        ]
        # sort by date
        data.sort(key=lambda x: x[3], reverse=False)
        Menu.display(
            "List of Ignored Pages",
            headers,
            data,
        )

    @classmethod
    def _get_func_file_path(cls) -> str:
        func_php_file_path = WPPaths.get_theme_path() / "inc/func.php"
        if not func_php_file_path.exists():
            Print.error(f"Function file {func_php_file_path} not found.")  # noqa: F821
            exit(1)
        return str(func_php_file_path)
