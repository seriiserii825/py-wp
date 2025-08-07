from pathlib import Path
from dto.RandomFieldDto import RandomFieldDto


class RandomFieldService:
    def __init__(self, wp_paths):
        self.wp_paths = wp_paths

    def get_random_fields(self) -> list[RandomFieldDto]:
        path = Path(self.wp_paths.get_script_dir_path()) / \
            "contact_forms" / "random_fields.csv"
        result = []

        with path.open("r") as f:
            for line in f:
                fields = line.strip().split(",")
                result.append(RandomFieldDto(name=fields[0], value=fields[1:]))

        return result
