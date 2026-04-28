from classes.utils.Command import Command


def update_translations():
    Command.run("wp language core update")
    Command.run("wp language plugin --all update")
    Command.run("wp language theme --all update")
