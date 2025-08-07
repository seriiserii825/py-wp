from classes.contact_form.ContactForm import ContactForm
from main_menu.contact_form_submenu import contact_form_submenu


def contact_form_menu():
    contact_form = ContactForm.get_contact_form()
    form_files_paths = ContactForm.form_to_files(contact_form)
    ContactForm.check_honeypot(form_files_paths)
    all_fields = ContactForm.get_required_fields(form_files_paths).all_fields
    required_fields = ContactForm.get_required_fields(form_files_paths).required_fields
    submitted_fields = ContactForm.get_submited_fields(form_files_paths)
    random_fields = ContactForm.get_random_fields()
    ContactForm.check_random_fields(all_fields, random_fields, submitted_fields)
    contact_form_submenu(
        form_files_paths,
        all_fields,
        required_fields,
        submitted_fields
    )
