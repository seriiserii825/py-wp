import os
from typing_extensions import List
from classes.utils.Command import Command
from classes.utils.WPPaths import WPPaths
from dto.PageDto import PageDto


class Page:
    pages: List[PageDto] = []

    @staticmethod
    def get_page_list() -> List[PageDto]:  # noqa: F821
        data = Command.run_json("wp post list --post_type=page --format=json")
        return [PageDto(**item) for item in data]

    @staticmethod
    def list_pages():
        command = "wp post list --post_type=page"
        Command.run(command)

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
        command = "wp post create --post_type=page"
        f" --post_status=publish --post_title='{title}'"
        Command.run(command)

    @staticmethod
    def create_multiple():
        titles = input("Enter the titles separated by commas: ")
        print(titles)
        titles = titles.split(",")
        for title in titles:
            title = title.strip()
            command = "wp post create --post_type=page"
            f"--post_status=publish --post_title='{title}'"
            Command.run(command)

    @staticmethod
    def delete_one():
        command = "wp post list --post_type=page"
        Command.run(command)
        ids = input("Enter the id of the page you want to delete: ")
        delete_command = f"wp post delete {ids} --force"
        Command.run(delete_command)

    @staticmethod
    def delete_multiple():
        command = "wp post list --post_type=page"
        Command.run(command)
        ids = input(
            "Enter the ids of the pages you want to delete separated by commas: "
        )
        ids = ids.split(",")
        for id in ids:
            Command.run(f"wp post delete {id} --force")

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
