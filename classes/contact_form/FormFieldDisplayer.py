from classes.utils.Menu import Menu


class FormFieldDisplayer:
    def show(self,
             all_fields: list[str],
             required_fields: list[str],
             submitted_fields: list[str]) -> None:
        sorted_submitted = [f for f in all_fields if f in submitted_fields]
        sorted_submitted += [f for f in submitted_fields if f not in all_fields]

        table_rows = []
        for field in sorted_submitted:
            if field in required_fields:
                table_rows.append([field, field, field])
            else:
                table_rows.append([field, "[red]No required", field])

        Menu.display(
            title="Contact Form Fields",
            columns=["All fields", "Required fields", "Submitted fields"],
            rows=table_rows,
            row_styles={"color": "blue"},
        )
