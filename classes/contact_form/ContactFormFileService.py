from classes.contact_form.form_dto.FormFilesDto import FormFilesDto


class ContactFormFileService:
    def __init__(self, command):
        self.command = command

    def extract_form_files(self, form) -> FormFilesDto:
        form_id = form.id
        base_path = form.form_folder_path

        html_path = f"{base_path}/html.txt"
        mail_path = f"{base_path}/mail.txt"

        self.command.run(f"wp post meta get {form_id} _form --allow-root > {html_path}")
        self.command.run(f"wp post meta get {form_id} _mail --allow-root > {mail_path}")

        return FormFilesDto(html=html_path, mail=mail_path)
