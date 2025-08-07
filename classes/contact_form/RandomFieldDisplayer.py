from classes.utils.Menu import Menu


class RandomFieldDisplayer:
    def show(self, random_fields: list) -> None:
        rows = [[rf.name, ", ".join(rf.value)] for rf in sorted(
            random_fields, key=lambda x: x.name)]

        Menu.display(
            title="Random Fields",
            columns=["Field", "Values"],
            rows=rows,
            row_styles={"color": "blue"},
        )
