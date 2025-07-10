from rich import print


class Print:
    @staticmethod
    def info(message):
        print(f"====== [blue]{message} ======")

    @staticmethod
    def success(message):
        print(f"[green]{message}")

    @staticmethod
    def error(message):
        print("=" * 20)
        print(f"[red]{message}")
        print("=" * 20)
