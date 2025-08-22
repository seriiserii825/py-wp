from acf.section.new_section import new_section
from acf.section.select_section import select_section
from acf.section.show_sections import show_sections
from classes.acf.AcfTransfer import AcfTransfer
from classes.utils.Menu import Menu
from classes.utils.Print import Print


def acf_func():
    AcfTransfer.wp_export()
    show_sections()
    _choose_section()


def _choose_section():
    menu_options = ["Select section", "Edit Section", "Create new section", "Exit"]
    choice = Menu.select_with_fzf(menu_options)

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
        Print.error("Exiting ACF CLI.")
        return
