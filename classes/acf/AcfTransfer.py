from classes.utils.Command import Command


class AcfTransfer:
    @staticmethod
    def wp_export():
        Command.run("rm -rf acf")
        Command.run("wp acf export --all")

    @staticmethod
    def wp_import():
        Command.run("wp acf clean")
        Command.run("wp acf import --all")
