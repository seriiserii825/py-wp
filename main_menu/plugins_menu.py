from classes.csv.BasePluginsCsv import BasePluginsCsv
from classes.csv.OtherPluginsCsv import OtherPluginsCsv


def plugins_menu():
    bp = BasePluginsCsv()
    bp.print_plugins()
    op = OtherPluginsCsv()
    op.print_plugins()
