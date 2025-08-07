from classes.contact_form.ContactForm import ContactForm
from rich import print


def contact_form_submenu(
    form_files_paths, all_fields, required_fields, submited_fields
):
    print("[blue]1. Show contact form fields")
    print("[green]2. Show files")
    print("[blue]3. Show random_fields")
    print("[yellow]4. Generate email")
    print("[red]5. Exit")

    option = input("Select an option: ")
    if option == "1":
        ContactForm.show_contact_form_fields(
            all_fields, required_fields, submited_fields
        )
        contact_form_submenu(
            form_files_paths, all_fields, required_fields, submited_fields
        )
    elif option == "2":
        ContactForm.show_contact_form_files(form_files_paths)
        contact_form_submenu(
            form_files_paths,
            all_fields,
            required_fields,
            submited_fields,
        )
    elif option == "3":
        ContactForm.show_random_fields()
        contact_form_submenu(
            form_files_paths,
            all_fields,
            required_fields,
            submited_fields,
        )
    # elif option == "4":
    #     generateEmail(all_fields, form_files_paths, project_folder)
    #     submenu(
    #         form_files_paths,
    #         all_fields,
    #         required_fields,
    #         submited_fields,
    #         project_folder,
    #     )
    # else:
    #     print("[red]Invalid option")
    #     exit()
