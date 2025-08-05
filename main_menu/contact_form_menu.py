from classes.contact_form.ContactForm import ContactForm


def contact_form_menu():
    contact_form = ContactForm.get_contact_form()
    print(f"contact_form: {contact_form}")
