from rich.console import Console
from rich.table import Table


class MyTable:
    def __init__(self):
        self.console = Console()

    def show(self, title: str, columns, rows, *, row_styles={}):
        """
        Print a Rich table.

        Parameters
        ----------
        title : str
            Table title.
        columns : list[dict]
            Each dict must have keys "title" and "style".
        rows : list[list[str]]
            2‑D list of cell values.
        row_styles : dict[int, str] | None
            Map of row index → Rich style string.
            Example: {0: "bold green", 3: "bright_red"}
            (row index is **zero‑based** inside this method)
        """

        table = Table(title=title, show_lines=False, expand=False)

        for col in columns:
            table.add_column(col)

        for idx, row in enumerate(rows):
            style = row_styles.get(idx, "")
            table.add_row(*row, style=style)

        self.console.print(table)
