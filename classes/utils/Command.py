import subprocess


class Command:
    @staticmethod
    def run(cmd: str) -> str:
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                check=True,
                text=True,
                capture_output=True,
            )
            print(f"Command: {cmd} executed successfully.")
            if result.stdout.strip():
                print(f"Command output: {result.stdout.strip()}")
            return result.stdout.strip()

        except subprocess.CalledProcessError as err:
            # Ruff writes lint errors to stdout, many other tools use stderr.
            output = (err.stderr or err.stdout).strip()
            # ➜ raise a *plain* message; style it where you print it
            raise RuntimeError(f"Command '{cmd}' failed with:\n{output}") from err
