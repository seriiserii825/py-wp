import subprocess


class Notification:
    def __init__(self, title: str, message: str):
        self.title = title
        self.message = message

    def notify(self):
        subprocess.run(["notify-send", self.title, self.message])
