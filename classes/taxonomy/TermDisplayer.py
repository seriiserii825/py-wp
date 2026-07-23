from classes.utils.Menu import Menu
from dto.TermDto import TermDto


class TermDisplayer:
    @staticmethod
    def display(title: str, terms: list[TermDto]):
        headers = ["ID", "Title", "Slug"]
        data = [
            [str(t.term_id), t.name, t.slug]
            for t in sorted(terms, key=lambda x: x.name)
        ]
        Menu.display(title, headers, data)
