from classes.pages.PageManager import PageManager
from classes.utils.Menu import Menu
from dto.PageDto import PageDto


class PageDisplayer:
    @staticmethod
    def display(title: str, pages: list[PageDto]):
        templates = PageManager.get_templates()
        names_by_file = {file: name for name, file in templates.items()}

        headers = ["ID", "Title", "Slug", "Status", "Template", "Date"]
        data = [
            [
                str(p.ID),
                p.post_title,
                p.post_name,
                p.post_status,
                names_by_file.get(p.page_template, p.page_template),
                p.post_date,
            ]
            for p in sorted(pages, key=lambda x: x.post_date)
        ]
        Menu.display(title, headers, data)
