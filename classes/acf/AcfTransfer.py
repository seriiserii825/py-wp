from classes.utils.Command import Command
from classes.utils.Print import Print


class AcfTransfer:
    @staticmethod
    def wp_export():
        try:
            Command.run_quiet("wp db check")  # check DB connection
            Command.run("rm -rf acf")
            Command.run("wp acf export --all")
        except RuntimeError as e:
            Print.error(f"Error during ACF export: {e}")
            exit(1)

    @staticmethod
    def wp_import():
        try:
            Command.run_quiet("wp db check")  # check DB connection
            Command.run("wp acf clean")
            Command.run("wp acf import --all")
        except RuntimeError as e:
            Print.error(f"Error during ACF import: {e}")
            exit(1)
