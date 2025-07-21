from classes.utils.InputValidator import InputValidator
from classes.utils.Print import Print


class FieldDeleter:
    def __init__(self, repo, mover):
        self.repo = repo
        self.mover = mover

    def delete_single(self, data, fields):
        try:
            index_path_str = "Enter field index to delete (e.g. 1.2): "
            index_path = self._get_index_path(index_path_str)
            confirm = self._confirm(
                "Are you sure you want to delete field at index"
                f" '{index_path}'? (y/n): "
            )
            if not confirm:
                Print.info("Delete cancelled.")
                return

            self.mover.pop_field(fields, index_path)
            Print.success("Field deleted successfully.")
            self.repo.save(data)
            Print.success("Field deleted and saved.")
        except IndexError:
            Print.error("Invalid index. No field deleted.")
        except Exception as e:
            Print.error(f"Error deleting field: {e}")

    def delete_multiple(self, data, fields):
        try:
            index_path_input = InputValidator.get_string(
                "Enter field indices to delete "
                "(comma-separated, from bigger to smaller, e.g. 3.2,3.1,3): "
            )
            index_strs = [s.strip() for s in index_path_input.split(",") if s.strip()]
            index_paths = [self.mover.parse_index_path(s) for s in index_strs]

            if not index_paths:
                Print.error("No valid indices provided.")
                return

            if self._has_prefix_conflicts(index_paths):
                return

            confirm = self._confirm(
                f"Are you sure you want to delete these "
                f"{len(index_paths)} field(s)? (y/n): "
            )
            if not confirm:
                Print.info("Delete cancelled.")
                return

            index_paths.sort(reverse=True)
            for path in index_paths:
                try:
                    deleted = self.mover.pop_field(fields, path)
                    label = deleted.get("label", deleted.get("name", "Unnamed"))
                    Print.success(
                        f"Deleted: {label} at index {'.'.join(map(str, path))}"
                    )
                except Exception as e:
                    Print.error(
                        f"Failed to delete at index {'.'.join(map(str, path))}: {e}"
                    )

            self.repo.save(data)
            Print.success("All selected fields deleted and saved.")

        except Exception as e:
            Print.error(f"Error during deletion: {e}")

    def _get_index_path(self, prompt: str) -> list:
        index_str = InputValidator.get_string(prompt)
        return self.mover.parse_index_path(index_str)

    def _confirm(self, message: str) -> bool:
        return InputValidator.get_bool(message)

    def _has_prefix_conflicts(self, index_paths: list) -> bool:
        def is_prefix(shorter, longer):
            return len(shorter) < len(longer) and longer[: len(shorter)] == shorter

        for i, path1 in enumerate(index_paths):
            for j, path2 in enumerate(index_paths):
                if i != j and (is_prefix(path1, path2) or is_prefix(path2, path1)):
                    Print.error(
                        f"Invalid index combination: "
                        f"{'.'.join(map(str, path1))} and {'.'.join(map(str, path2))} "
                        f"cannot be deleted together."
                    )
                    return True
        return False
