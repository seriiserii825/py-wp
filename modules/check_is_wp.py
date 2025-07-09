import os


def check_is_wp():
    if not os.path.exists("front-page.php"):
        print("This is not a WordPress project."
              " Please run this command in the root of your WordPress project.")
