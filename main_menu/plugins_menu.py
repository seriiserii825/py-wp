from classes.csv.BasePluginsCsv import BasePluginsCsv
from classes.csv.OtherPluginsCsv import OtherPluginsCsv
from classes.plugin.Plugin import Plugin
from classes.utils.ColorMenu import ColorMenu


def plugins_menu():
    rows = [
        "[green]List installed",
        "[green]List base from csv file",
        "[green]List other from csv file",
        "[blue]Install base",
        "[blue]Install other",
        "[red]Uninstall",
    ]
    choice = ColorMenu.select(rows)

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
