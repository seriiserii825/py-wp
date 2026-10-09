from typing import List

from rich.markup import escape

from classes.utils.ColorMenu import ColorMenu


class SectionMenu:
    title = ""
    labels: List[str] = []

    @staticmethod
    def display(title: str, columns: List[str], rows: List[List[str]]):
        """
        Remember the options; choose_option() shows them in a colored fzf
        menu (last column of each row is the label, columns are unused).
        """
        SectionMenu.title = title
        SectionMenu.labels = [
            f"[{'blue' if i % 2 == 0 else 'green'}]{escape(row[-1])}"
            for i, row in enumerate(rows)
        ]

    @staticmethod
    def choose_option() -> int:
        """
        Index of the chosen row. A choice is required (callers index the
        rows with it), so Esc shows the menu again.
        """
        while True:
            choice = ColorMenu.select(
                SectionMenu.labels, title=SectionMenu.title, exit_label=None
            )
            if choice != -1:
                return choice
