from rich import print


class InputValidator:
    def _pretty_print(self, value):
        print("[green]============================")
        print(f"Value: {value}")
        print("[green]============================")

    @staticmethod
    def get_int(prompt="Enter an integer: "):
        while True:
            try:
                return int(input(prompt))
            except ValueError:
                print("Invalid input. Please enter a valid integer.")

    @staticmethod
    def get_float(prompt="Enter a number: "):
        while True:
            try:
                return float(input(prompt))
            except ValueError:
                print("Invalid input. Please enter a valid number.")

    @staticmethod
    def get_string(prompt="Enter text: ", allow_empty=False):
        while True:
            value = input(prompt).strip()
            if value or allow_empty:
                return value
            print("Input cannot be empty. Try again.")

    @staticmethod
    def get_bool(prompt="Enter 'y' for yes or 'n' for no: "):
        while True:
            value = input(prompt).strip().lower()
            if value in ('y', 'yes'):
                return True
            elif value in ('n', 'no'):
                return False
            print("Invalid input. Please enter 'y' or 'n'.")
