from classes.pages.PageDisplayer import PageDisplayer
from classes.pages.PageFileHandler import PageFileHandler
from classes.pages.PageManager import PageManager
from classes.pages.PageSelector import PageSelector
from classes.utils.Command import Command
from classes.utils.Print import Print
from dto.PageDto import PageDto


class Page:
    pages: list[PageDto] = []

    @classmethod
    def list_all(cls):
        raw_pages = Command.run_json("wp post list --post_type=page --format=json")
        cls.pages = [PageDto(**p) for p in raw_pages]
        PageDisplayer.display("List of Pages", cls.pages)

    @classmethod
    def ignore_page(cls):
        cls.list_all()
        ignored_ids = PageFileHandler.get_ignored_ids()
        unignored = [p for p in cls.pages if p.ID not in ignored_ids]
        if not unignored:
            Print.error("All pages already ignored.")
            return

        selected = PageSelector.select_pages(unignored)
        if selected:
            PageFileHandler.add_ignored_id(selected[0])
            Print.success(f"Ignored page ID {selected[0]}")

        ignored_ids = PageFileHandler.get_ignored_ids()
        PageDisplayer.display(
            "Ignored Pages",
            [p for p in cls.pages if p.ID in ignored_ids],
        )

    @classmethod
    def create_one(cls):
        title = input("Enter page title: ").strip()
        if not title:
            Print.error("Title cannot be empty.")
            return
        PageManager.create(title)
        Print.success(f"Page '{title}' created successfully.")

    @classmethod
    def create_many(cls):
        titles = input("Enter page titles (comma-separated): ").strip().split(",")
        if not titles:
            Print.error("No titles provided.")
            return
        PageManager.create_many(titles)
        Print.success(f"Created {len(titles)} pages successfully.")

    @classmethod
    def delete(cls):
        cls.list_all()
        if not cls.pages:
            Print.error("No pages available to delete.")
            return

        selected = PageSelector.select_with_fzf(cls.pages)
        if not selected:
            Print.error("No pages selected for deletion.")
            return

        for page_id in selected:
            PageManager.delete(page_id)
            Print.success(f"Deleted page ID {page_id}")

    @classmethod
    def delete_multiple(cls):
        cls.list_all()
        if not cls.pages:
            Print.error("No pages available to delete.")
            return

        selected = PageSelector.select_with_fzf(cls.pages)
        if not selected:
            Print.error("No pages selected for deletion.")
            return

        for page_id in selected:
            PageManager.delete(page_id)
            Print.success(f"Deleted page ID {page_id}")

    @classmethod
    def get_page_by_id(cls, page_id: int) -> PageDto:
        for page in cls.pages:
            if page.ID == page_id:
                return page
        raise ValueError(f"Page with ID {page_id} not found.")
