from classes.csv.CsvPlugin import CsvPlugin


def plugins_menu():
    csv_cl = CsvPlugin()
    csv_cl.print_base_plugins()
    csv_cl.print_other_plugins()
