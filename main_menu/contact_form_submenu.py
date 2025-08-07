from classes.contact_form.ContactForm import ContactForm
from rich import print


def contact_form_submenu(
    form_files_paths, all_fields, required_fields, submited_fields
):
    while True:
        print("\n[bold cyan]Contact Form Menu")
        print("[blue]1. Show contact form fields")
        print("[green]2. Show files")
        print("[blue]3. Show random fields")
        print("[red]4. Exit")

        option = input("Select an option: ").strip()

        match option:
            case "1":
                ContactForm.show_contact_form_fields(
                    all_fields, required_fields, submited_fields
                )
            case "2":
                ContactForm.show_contact_form_files(form_files_paths)
            case "3":
                ContactForm.show_random_fields()
            case "4":
                print("[bold red]Exiting menu...")
                break
            case _:
                print("[red]Invalid option. Please try again.")
