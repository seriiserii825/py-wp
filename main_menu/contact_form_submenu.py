from classes.contact_form.ContactForm import ContactForm
from main_menu.table_menu import table_menu


def contact_form_submenu(
    form_files_paths, all_fields, required_fields, submited_fields
):
    options = [
        "Show contact form fields",
        "Show files",
        "Show random fields",
    ]
    while True:
        match table_menu("Contact Form", options):
            case 0:
                ContactForm.show_contact_form_fields(
                    all_fields, required_fields, submited_fields
                )
            case 1:
                ContactForm.show_contact_form_files(form_files_paths)
            case 2:
                ContactForm.show_random_fields()
            case _:  # Back
                break
