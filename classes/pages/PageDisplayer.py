from classes.utils.Menu import Menu
from dto.PageDto import PageDto


class PageDisplayer:
    @staticmethod
    def display(title: str, pages: list[PageDto]):
        headers = ["ID", "Title", "Status", "Date"]
        data = [
            [str(p.ID), p.post_title, p.post_status, p.post_date]
            for p in sorted(pages, key=lambda x: x.post_date)
        ]
        Menu.display(title, headers, data)
