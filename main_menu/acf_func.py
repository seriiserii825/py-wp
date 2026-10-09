from acf.section.new_section import new_section
from acf.section.select_section import select_section
from acf.section.show_sections import show_sections
from classes.acf.AcfTransfer import AcfTransfer
from classes.utils.ExitApp import ExitApp
from classes.utils.ColorMenu import ColorMenu
from py_libs.Print import Print


def acf_func(to_import: bool = False):
    if to_import:
        AcfTransfer.wp_import()
    else:
        AcfTransfer.wp_export()
    show_sections()
    _choose_section()


def _choose_section():
    menu_options = [
        "[green]Select section",
        "[yellow]Edit Section",
        "[blue]Create new section",
        "[red]Delete Section",
        "[red]Back",
    ]
    choice = ColorMenu.select(menu_options, esc=4)

    if choice == 0:
        Print.info("Select section selected.")
        select_section()
    elif choice == 1:
        from classes.acf.section.EditSection import EditSection

        Print.info("Edit section selected.")
        EditSection.edit_location()
    elif choice == 2:
        Print.info("Create new section selected.")
        new_section()
    elif choice == 3:
        from classes.acf.section.EditSection import EditSection

        Print.info("Delete section selected.")
        EditSection.delete_section()
    elif choice == 4:
        Print.info("Going back.")
        return
    elif choice == 5:
        ExitApp.confirm_and_exit()
        _choose_section()
