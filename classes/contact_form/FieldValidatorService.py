from rich import print

from dto.RandomFieldDto import RandomFieldDto


class FieldValidatorService:
    def validate(self,
                 all_fields: list[str],
                 random_fields: list[RandomFieldDto],
                 submitted_fields: list[str]) -> bool:
        random_set = set(field.name for field in random_fields)
        submitted_set = set(submitted_fields)
        all_set = set(all_fields)

        missing_in_random = all_set - random_set
        missing_in_submitted = all_set - submitted_set
        extra_in_submitted = submitted_set - all_set

        if missing_in_random:
            print("[red]HTML fields not in random:")
            for field in missing_in_random:
                print(f"[red]{field}")
            return False

        if missing_in_submitted:
            print("[red]HTML fields not in submitted:")
            for field in missing_in_submitted:
                print(f"[red]{field}")
            return False

        if extra_in_submitted:
            print("[red]Submitted fields not in HTML:")
            for field in extra_in_submitted:
                print(f"[red]{field}")
            return False

        return True
