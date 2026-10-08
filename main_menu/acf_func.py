from acf.section.new_section import new_section
from acf.section.select_section import select_section
from acf.section.show_sections import show_sections
from classes.acf.AcfTransfer import AcfTransfer
from main_menu.table_menu import table_menu
from py_libs.Print import Print


def acf_func(to_import: bool = False):
    if to_import:
        AcfTransfer.wp_import()
    else:
        AcfTransfer.wp_export()
    show_sections()
    _choose_section()


def _choose_section():
    menu_options = ["Select section",
                    "Edit Section", "Create new section", "Delete Section"]
    choice = table_menu("ACF", menu_options, red_options={"Delete Section"})

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
    # Back → return to the main menu
