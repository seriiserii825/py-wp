def show_field_data():
    from classes.acf.field.FieldMenu import FieldMenu
    import os

    section_file_json_path = "path/to/your/section_file.json"  # Update this path as needed

    if not os.path.exists(section_file_json_path):
        print(f"The file '{section_file_json_path}' does not exist.")
        return

    FieldMenu.init(section_file_json_path)
    FieldMenu.show_all()
    FieldMenu.create_field()
