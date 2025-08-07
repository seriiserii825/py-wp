from pathlib import Path

from classes.contact_form.form_dto.FormFilesDto import FormFilesDto
from classes.utils.Command import Command
from classes.utils.Select import Select
from classes.utils.WPPaths import WPPaths
from dto.ContactFormDto import ContactFormDto


class ContactForm:
    @staticmethod
    def get_contact_form() -> ContactFormDto:
        script_dir_path = WPPaths.get_script_dir_path()
        theme_path = WPPaths.get_theme_path()
        theme_name = f"{theme_path.name}"
        csv_file_path = Path(f"{script_dir_path}/contact_forms/{theme_name}.csv")
        if not csv_file_path.parent.exists():
            csv_file_path.parent.mkdir(parents=True, exist_ok=True)
        command = (
            f"wp post list --post_type=wpcf7_contact_form --format=csv "
            f"--allow-root > {csv_file_path}"
        )
        Command.run(command)
        result = []
        with open(csv_file_path, "r") as f:
            lines = f.readlines()
            for index, line in enumerate(lines):
                if index == 0:
                    continue
                fields = line.split(",")
                result.append(f"{fields[1]}-{fields[0]}")
        selected_form = Select.select_one(result)
        replaced_symbols = [
            " ",
            "(",
            ")",
            "/",
            "\\",
            ":",
            "*",
            "?",
            '"',
            "<",
            ">",
        ]
        form_name = selected_form.split("-")[0].lower()
        for symbol in replaced_symbols:
            form_name = form_name.replace(symbol, "-")
        form_id = selected_form.split("-")[1]
        script_dir_path = WPPaths.get_script_dir_path()
        form_folder_path = str(
            Path(f"{script_dir_path}/{theme_name}/{form_name}-{form_id}")
        )
        if not Path(form_folder_path).exists():
            Path(form_folder_path).mkdir(parents=True, exist_ok=True)
        return ContactFormDto(
            id=form_id,
            title=form_name,
            csv_file_path=str(csv_file_path),
            form_folder_path=form_folder_path,
        )

    @staticmethod
    def formToFiles(form: ContactFormDto) -> FormFilesDto:
        form_id = form.id
        form_html_path = form.form_folder_path + "/html.txt"
        command = f"wp post meta get {form_id} _form --allow-root > {form_html_path}"
        Command.run(command)

        form_file_path = form.form_folder_path + "/mail.txt"
        command = f"wp post meta get {form_id} _mail --allow-root > {form_file_path}"
        Command.run(command)
        return FormFilesDto(
            html=form_html_path,
            mail=form_file_path,
        )
