from classes.utils.Select import Select
from dto.PageDto import PageDto


class PageSelector:
    @staticmethod
    def select_pages(pages: list[PageDto]) -> list[int]:
        options = [f"{page.ID}-{page.post_title}" for page in pages]
        selected = Select.select_multiple(options)
        return [int(item.split("-")[0]) for item in selected]

    @staticmethod
    def select_with_fzf(pages: list[PageDto]) -> list[int]:
        options = [f"{page.ID}-{page.post_title}" for page in pages]
        selected = Select.select_with_fzf(options)
        return [int(item.split("-")[0]) for item in selected]
