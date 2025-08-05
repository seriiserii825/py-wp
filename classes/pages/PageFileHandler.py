from classes.utils.Print import Print
from classes.utils.WPPaths import WPPaths


class PageFileHandler:
    @staticmethod
    def get_func_file_path() -> str:
        path = WPPaths.get_theme_path() / "inc/func.php"
        if not path.exists():
            Print.error(f"{path} not found.")
            exit(1)
        return str(path)

    @staticmethod
    def get_ignored_ids() -> list[int]:
        with open(PageFileHandler.get_func_file_path()) as f:
            for line in f:
                if "$ids" in line:
                    ids_str = line.split("=")[1].strip().rstrip(";").strip("[]")
                    return [
                        int(id.strip())
                        for id in ids_str.split(",")
                        if id.strip().isdigit()
                    ]
        return []

    @staticmethod
    def add_ignored_id(new_id: int):
        path = PageFileHandler.get_func_file_path()
        with open(path, "r") as f:
            lines = f.readlines()

        updated = []
        for line in lines:
            if "$ids" in line:
                line = line.replace("];", f",{new_id}];")
            updated.append(line)

        with open(path, "w") as f:
            f.writelines(updated)
