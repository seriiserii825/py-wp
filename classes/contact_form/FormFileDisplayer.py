class FormFileDisplayer:
    def __init__(self, command):
        self.command = command

    def show(self, html_path: str, mail_path: str) -> None:
        self.command.run(f"bat {html_path}")
        self.command.run(f"bat {mail_path}")
