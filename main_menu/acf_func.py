from classes.acf.AcfTransfer import AcfTransfer
from classes.utils.Menu import Menu
from classes.utils.Print import Print


def acf_func():
    # AcfTransfer.wp_export()

    header = ["Index", "Option"]

    rows = [
        ["0", "Create new section"],
        ["1", "Select section"],
        ["2", "Exit"]
    ]

    Menu.display("Welcome to ACF CLI", header, rows)
    choice = Menu.choose_option()

    if choice == 0:
        Print.info("Create new section selected.")
        # newSection()
    elif choice == 1:
        Print.info("Select section selected.")
        # wpImport()
    elif choice == 2:
        Print.error("Exiting ACF CLI.")
        exit()
