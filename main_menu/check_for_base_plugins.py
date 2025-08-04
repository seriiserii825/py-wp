from classes.csv.BasePluginsCsv import BasePluginsCsv
from classes.plugin.Plugin import Plugin
from classes.utils.Print import Print


def check_for_base_plugins():
    bp = BasePluginsCsv()
    is_base_plugins_installed = bp.is_base_plugins_installed()
    if not is_base_plugins_installed:
        Print.error("Base plugins are not installed. Installing them now...")
        pi = Plugin()
        pi.install_all_plugins(bp.get_plugin_dtos())
    else:
        Print.info("Base plugins are already installed.")
