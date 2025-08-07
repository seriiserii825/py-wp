import os

from classes.utils.Command import Command
from classes.utils.Print import Print


def check_is_wp():
    if not os.path.exists("style.css"):
        Print.error(
            "This is not a WordPress project."
            " Please run this command in the root of your WordPress project."
        )
        exit(1)

    try:
        Command.run("wp core is-installed")
    except RuntimeError as e:
        Print.error(f"Error: {e}")
        exit(1)
