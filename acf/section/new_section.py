from classes.acf.section.Section import Section


def new_section():
    Section.add_name_and_file_path()
    # choice = Section.choose_type()
    #
    # if choice == 1:
    #     Section.new_acf_page()
    #     wpImport()
    # elif choice == 2:
    #     Section.new_acf_custom_post_type()
    #     wpImport()
    # elif choice == 3:
    #     Section.new_acf_taxonomy()
    #     wpImport()
    # else:
    #     Print.error("Invalid choice. Please try again.")
    #     return
