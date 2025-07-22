from classes.acf.section.SelectSection import SelectSection


def show_sections():
    sections_files = SelectSection.get_sections_files()
    if not sections_files:
        print("No sections found.")
        return
    print("Available sections:")
    for index, file in enumerate(sections_files):
        print(f"{index + 1}. {file}")
