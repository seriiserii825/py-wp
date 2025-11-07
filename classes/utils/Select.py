import subprocess
from typing import List

import questionary
from simple_term_menu import TerminalMenu


class Select:
    @staticmethod
    def select_with_fzf(options) -> list[str]:
        input_text = "\n".join(options)
        result = subprocess.run(
            ["fzf", "--multi", "--height", "40%", "--reverse"],
            input=input_text.encode(),
            stdout=subprocess.PIPE,
        )
        selected = result.stdout.decode().strip().split("\n")
        return selected if selected != [""] else []

    @staticmethod
    def select_questionary(options: List[str]) -> List[str]:
        selected = questionary.checkbox("Select options:", choices=options).ask()
        return selected

    @staticmethod
    def select_multiple(options: List[str]) -> List[str]:
        terminal_menu = TerminalMenu(
            options,
            multi_select=True,
            show_multi_select_hint=True,
            show_search_hint=True,
            preview_command="bat --color=always {}",
            preview_size=0.75,
        )
        result = terminal_menu.show()
        print(f"result: {result}")
        selected = terminal_menu.chosen_menu_entries or []
        return selected

    @staticmethod
    def select_one(options):
        terminal_menu = TerminalMenu(options)
        # menu_entry_index = terminal_menu.show()
        menu_entry_index = terminal_menu.show()
        return options[menu_entry_index]
