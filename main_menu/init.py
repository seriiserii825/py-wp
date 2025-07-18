import os
import subprocess


def init():
    user = os.getenv("USER")
    path_to_wp_init = (
        "/home/" + str(user) + "/Documents/python/py-wp/bash-scripts/wp-init.sh"
    )
    subprocess.call(path_to_wp_init, shell=True)


def resetSettings():
    user = os.getenv("USER")
    path_to_wp_init = (
        "/home/" + str(user) + "/Documents/python/py-wp/bash-scripts/wp-reset.sh"
    )
    subprocess.call(path_to_wp_init, shell=True)
