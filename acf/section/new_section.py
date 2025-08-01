from classes.acf.AcfTransfer import AcfTransfer
from classes.acf.section.CreateSection import CreateSection
from classes.exception.NewSectionException import NewSectionException
from classes.utils.Print import Print


def new_section():
    CreateSection.show_all_files()
    try:
        CreateSection.add_name_and_file_path()
        choice = CreateSection.choose_type()
    except NewSectionException as e:
        Print.error(str(e))
        return

    if choice == 0:
        CreateSection.new_acf_page()
        AcfTransfer.wp_import()
    elif choice == 1:
        CreateSection.new_acf_custom_post_type()
        AcfTransfer.wp_import()
    elif choice == 2:
        CreateSection.new_acf_taxonomy()
        AcfTransfer.wp_import()
    elif choice == 3:
        CreateSection.new_acf_options_page()
        # AcfTransfer.wp_import()
    else:
        Print.error("Invalid choice. Please try again.")
        return
