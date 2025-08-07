from pathlib import Path


class FileWriter:
    @staticmethod
    def write_file(path: Path, content: str):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
