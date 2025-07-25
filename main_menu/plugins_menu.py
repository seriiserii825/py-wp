from classes.csv.BasePluginsCsv import BasePluginsCsv
from classes.csv.OtherPluginsCsv import OtherPluginsCsv
from classes.plugin.Plugin import Plugin
from classes.utils.Menu import Menu


def plugins_menu():
    headers = ["Index", "Description"]
    rows = [
        ["0", "List installed plugins"],
        ["1", "List base plugins from csv file"],
        ["2", "List other plugins from csv file"],
        ["3", "Install all base plugins"],
        ["4", "Install from other plugins"],
        ["5", "Uninstall plugin"],
        ["6", "Exit"],
    ]

    Menu.display("Plugins Menu", headers, rows)
    choice = Menu.choose_option()
    print(f"choice: {choice}")

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
        pi.install_plugins(bp.get_plugin_dtos())
        plugins_menu()
    elif choice == 5:
        pi = Plugin()
        pi.uninstall_plugin()
        plugins_menu()
