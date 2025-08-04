from pathlib import Path
import subprocess
import json
import shlex

from classes.utils.Print import Print


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
            Print.success(f"Command: {cmd} executed successfully.")
            if result.stdout.strip():
                Print.info(f"Command output: {result.stdout.strip()}")
            return result.stdout.strip()

        except subprocess.CalledProcessError as err:
            # Ruff writes lint errors to stdout, many other tools use stderr.
            output = (err.stderr or err.stdout).strip()
            # ➜ raise a *plain* message; style it where you print it
            raise RuntimeError(f"Command '{cmd}' failed with:\n{output}") from err

    @staticmethod
    def run_quiet(cmd: str) -> str:
        """Run a command and return output, but suppress success logs."""
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                check=True,
                text=True,
                capture_output=True,
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as err:
            output = (err.stderr or err.stdout).strip()
            raise RuntimeError(f"Command '{cmd}' failed with:\n{output}") from err

    @staticmethod
    def run_json(cmd: str) -> list | dict:
        """Run a command expected to return JSON and parse it."""
        output = Command.run_quiet(cmd)
        try:
            return json.loads(output)
        except json.JSONDecodeError as err:
            raise ValueError(
                f"Failed to parse JSON output from '{cmd}':\n{output}"
            ) from err

    @staticmethod
    def build(cmd: str, *args: Path | str) -> str:
        quoted = [shlex.quote(str(a)) for a in args]
        return f"{cmd} {' '.join(quoted)}"
