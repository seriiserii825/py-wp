from pathlib import Path


class PathManager:
    def __init__(self):
        self.php_root = Path("template-parts")
        self.scss_modules_root = Path("src/modules")
        self.scss_entry_file = Path("src/scss/my.scss")

    def inject_scss_use(self, folder: str, filename: str):
        import_line = f'@use "modules/{folder}/{filename}";\\n'
        if self.scss_entry_file.exists():
            content = self.scss_entry_file.read_text()
            if import_line not in content:
                with self.scss_entry_file.open("a") as f:
                    f.write(import_line)
        else:
            self.scss_entry_file.parent.mkdir(parents=True, exist_ok=True)
            with self.scss_entry_file.open("w") as f:
                f.write(import_line)
