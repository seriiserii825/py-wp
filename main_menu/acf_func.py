from acf.section.new_section import new_section
from acf.section.select_section import select_section
from acf.section.show_sections import show_sections
from classes.acf.AcfTransfer import AcfTransfer
from classes.utils.InputValidator import InputValidator
from classes.utils.Menu import Menu
from classes.utils.Print import Print


def acf_func():
    to_import = InputValidator.get_bool(
        "Do you want to import ACF data, by default will be exported? (y/n): "
    )
    if to_import:
        AcfTransfer.wp_import()
    else:
        AcfTransfer.wp_export()

    header = ["Index", "Option"]
    rows = [
        ["0", "Create new section"],
        ["1", "Select section"],
        ["2", "Edit Section"],
        ["3", "Exit"],
    ]

    show_sections()

    Menu.display("Welcome to ACF CLI", header, rows)

    choice = Menu.choose_option()

    if choice == 0:
        Print.info("Create new section selected.")
        new_section()
    elif choice == 1:
        Print.info("Select section selected.")
        select_section()
    elif choice == 2:
        from classes.acf.section.EditSection import EditSection

        Print.info("Edit section selected.")
        EditSection.edit_location()
    elif choice == 3:
        Print.error("Exiting ACF CLI.")
        exit()
