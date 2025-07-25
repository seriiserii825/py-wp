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
    row_styles = {
        0: "bold blue",
        1: "bold blue",
        2: "bold blue",
        3: "bold green",
        4: "bold green",
        5: "bold red",
        6: "bold red",
    }
    Menu.display("Plugins Menu", headers, rows, row_styles=row_styles)
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
