import os

from classes.utils.Print import Print


def check_is_wp():
    if not os.path.exists("front-page.php"):
        Print.error(
            "This is not a WordPress project."
            " Please run this command in the root of your WordPress project."
        )
