from classes.csv.BasePluginsCsv import BasePluginsCsv
from classes.csv.OtherPluginsCsv import OtherPluginsCsv
from classes.plugin.Plugin import Plugin
from main_menu.table_menu import table_menu


def plugins_menu():
    options = [
        "List installed",
        "List base from csv file",
        "List other from csv file",
        "Install base",
        "Install other",
        "Uninstall",
    ]
    choice = table_menu("Plugins", options, red_options={"Uninstall"})

    if choice == 0:
        pi = Plugin()
        pi.list_installed_plugins()
        plugins_menu()
    elif choice == 1:
        bp = BasePluginsCsv()
        bp.print_plugins()
        plugins_menu()
    elif choice == 2:
        op = OtherPluginsCsv()
        op.print_plugins()
        plugins_menu()
    elif choice == 3:
        bp = BasePluginsCsv()
        pi = Plugin()
        pi.install_all_plugins(bp.get_plugin_dtos())
        plugins_menu()
    elif choice == 4:
        op = OtherPluginsCsv()
        pi = Plugin()
        pi.install_plugin_by_slug(op.get_plugin_dtos())
        plugins_menu()
    elif choice == 5:
        pi = Plugin()
        pi.uninstall_plugin()
        plugins_menu()
