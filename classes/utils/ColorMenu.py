from py_libs.Menu import Menu


class ColorMenu:
    @staticmethod
    def select(
        labels: list[str],
        title: str | None = None,
        exit_label: str | None = "[red]Exit",
        esc: int | None = None,
    ) -> int:
        """
        Colored fzf menu (py_libs.Menu.select_fzf_menu), 0-based result:
        labels[i] → i, "00) <exit_label>" → len(labels),
        Esc → esc (default: same as the exit item, or -1 without one).
        So the old `if choice == <last index>: exit` checks keep working.
        """
        choice = Menu.select_fzf_menu(labels, title, exit_label)
        if choice is None:
            if esc is not None:
                return esc
            return len(labels) if exit_label else -1
        if choice == 0:
            return len(labels)
        return choice - 1
