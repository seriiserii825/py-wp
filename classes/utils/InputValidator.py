from rich.console import Console

console = Console()


class InputValidator:
    def _pretty_print(self, value):
        console.print("[green]============================")
        console.print(f"Value: {value}")
        console.print("[green]============================")

    @staticmethod
    def get_int(prompt="Enter an integer: "):
        while True:
            try:
                return int(console.input(prompt))
            except ValueError:
                console.print("Invalid input. Please enter a valid integer.")

    @staticmethod
    def get_float(prompt="Enter a number: "):
        while True:
            try:
                return float(console.input(prompt))
            except ValueError:
                console.print("Invalid input. Please enter a valid number.")

    @staticmethod
    def get_positive_int(prompt="Enter a number: "):
        while True:
            value = console.input(prompt).strip()
            try:
                num = int(value)
            except ValueError:
                console.print("Invalid input. Please enter a valid number!")
                continue
            if num <= 0:
                console.print("Invalid input. Please enter a number greater than 0!")
                continue
            return num

    @staticmethod
    def get_string(prompt="Enter text: ", allow_empty=False):
        while True:
            value = console.input(prompt)
            value = value.strip()
            if value or allow_empty:
                return value
            console.print("Input cannot be empty. Try again.")

    @staticmethod
    def get_bool(prompt="Enter 'y' for yes or 'n' for no: "):
        while True:
            value = console.input(prompt).strip().lower()
            if value in ("y", "yes"):
                return True
            elif value in ("n", "no"):
                return False
            console.print("Invalid input. Please enter 'y' or 'n'.")

    @staticmethod
    def get_bool_true_default(prompt="Enter 'n' for no or 'y' by default: "):
        while True:
            value = console.input(prompt).strip().lower()
            if value in ("n", "no"):
                return False
            return True
