from typing_extensions import List
from classes.utils.Command import Command
from classes.utils.Menu import Menu
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
        pages_to_delete = [f"{page.ID}-{page.post_title}" for page in pages]
        selected_pages = Select.select_with_fzf(pages_to_delete)
        pages_id = [
            int(selected_page.split("-")[0]) for selected_page in selected_pages
        ]
        return pages_id

    @classmethod
    def ignore(cls):
        cls.list_pages()
        func_php_file_path = WPPaths.get_theme_path() / "inc/func.php"
        if not func_php_file_path.exists():
            print(f"File {func_php_file_path} does not exist.")
            return
        with open(func_php_file_path, "w") as file:
            lines = file.readlines()
            for line in lines:
                if "$ids" in line:
                    page_id = input("Enter the ID of the page to ignore: ")
                    line = line.replace("];", f",{page_id}];")
            file.write("".join(lines))
            print(f"Updated {func_php_file_path} with new page ID to ignore.")
