from classes.acf.AcfTransfer import AcfTransfer
from classes.acf.section.Section import Section
from classes.exception.NewSectionException import NewSectionException
from classes.utils.Print import Print


def new_section():
    Section.show_all_files()
    try:
        Section.add_name_and_file_path()
        choice = Section.choose_type()
    except NewSectionException as e:
        Print.error(str(e))
        return

    if choice == 1:
        Section.new_acf_page()
        AcfTransfer.wp_import()
    elif choice == 2:
        Section.new_acf_custom_post_type()
        AcfTransfer.wp_import()
    elif choice == 3:
        Section.new_acf_taxonomy()
        AcfTransfer.wp_import()
    else:
        Print.error("Invalid choice. Please try again.")
        return
