from typing_extensions import List
from classes.utils.Command import Command
from dto.PageDto import PageDto


class Page:
    pages: List[PageDto] = []

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
