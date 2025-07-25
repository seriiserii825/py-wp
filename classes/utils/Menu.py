from typing import List

from classes.utils.MyTable import MyTable
from classes.utils.Print import Print


class Menu:
    rows_count = 0

    @classmethod
    def display(
        cls, title: str, columns: List[str], rows: List[List[str]], row_styles=None
    ):
        """
        Display the main menu options.
        """

        cls.rows_count = 0
        cls.rows_count += len(rows)

        if row_styles is None:
            row_styles = {}

        tb = MyTable()
        tb.show(title, columns, rows, row_styles=row_styles)

    @classmethod
    def choose_option(cls):
        """
        Prompt the user to choose an option from the menu.
        """
        while True:
            try:
                count_range = (
                    f"Please enter a number between 0 and {cls.rows_count - 1}: "
                )
                choice = int(input(count_range))
                if choice in range(0, cls.rows_count):
                    return choice
                else:
                    print(
                        f"[red]Invalid input."
                        f"Enter a number between 0 and {cls.rows_count - 1}."
                    )
            except ValueError:
                Print.error("Input must be a number. Please try again.")
