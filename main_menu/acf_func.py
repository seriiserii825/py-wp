from acf.section.select_section import select_section
from classes.acf.AcfTransfer import AcfTransfer
from classes.utils.InputValidator import InputValidator


def acf_func():
    to_import = InputValidator.get_bool(
        "Do you want to import ACF data, by default will be exported? (y/n): "
    )
    if to_import:
        AcfTransfer.wp_import()
    else:
        AcfTransfer.wp_export()

    # header = ["Index", "Option"]
    # rows = [["0", "Create new section"], ["1", "Select section"], ["2", "Exit"]]
    # Menu.display("Welcome to ACF CLI", header, rows)

    select_section()

    # choice = Menu.choose_option()
    #
    # if choice == 0:
    #     Print.info("Create new section selected.")
    #     new_section()
    # elif choice == 1:
    #     select_section()
    #     Print.info("Select section selected.")
    # elif choice == 2:
    #     Print.error("Exiting ACF CLI.")
    #     exit()
