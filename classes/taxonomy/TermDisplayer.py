from classes.utils.Menu import Menu
from dto.TermDto import TermDto


class TermDisplayer:
    @staticmethod
    def display(title: str, terms: list[TermDto]):
        headers = ["ID", "Title", "Slug"]
        data = TermDisplayer._build_rows(terms)
        Menu.display(title, headers, data)

    @staticmethod
    def _build_rows(terms: list[TermDto]) -> list[list[str]]:
        children_by_parent: dict[int, list[TermDto]] = {}
        for term in terms:
            children_by_parent.setdefault(term.parent, []).append(term)
        for children in children_by_parent.values():
            children.sort(key=lambda t: t.name)

        rows: list[list[str]] = []

        def add_children(parent_id: int, depth: int) -> None:
            for term in children_by_parent.get(parent_id, []):
                indent = "  " * depth + ("└─ " if depth else "")
                rows.append(
                    [str(term.term_id), f"{indent}{term.name}", term.slug]
                )
                add_children(term.term_id, depth + 1)

        add_children(0, 0)
        return rows
