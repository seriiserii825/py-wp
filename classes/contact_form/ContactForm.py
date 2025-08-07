from pathlib import Path

from classes.contact_form.form_dto.FormFilesDto import FormFilesDto
from classes.utils.Command import Command
from classes.utils.Menu import Menu
from classes.utils.Print import Print
from classes.utils.Select import Select
from classes.utils.WPPaths import WPPaths
from dto.ContactFormDto import ContactFormDto
from dto.FormFieldsDto import FormFieldsDto
from dto.RandomFieldDto import RandomFieldDto


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

    @staticmethod
    def check_honeypot(form_files_paths: FormFilesDto) -> None:
        fields = []
        form_html = form_files_paths.html
        items = []
        with open(form_html, "r") as f:
            line = f.read().strip()
            fields = line.split("[")
            for field in fields:
                if "]" in field:
                    items.append(field.split("]")[0])
        # check for honeypot field if exists
        honeypot = [item for item in items if "honeypot" in item]
        if honeypot:
            Print.info(f"Honeypot field found: [green]{honeypot[0]}[/green]")
        else:
            Print.error("Honeypot field not found.")

    @staticmethod
    def get_required_fields(form_files_paths: FormFilesDto) -> FormFieldsDto:
        fields = []
        ignored_fields = ["timecheck_enabled", "honeypot", "acceptance", "submit"]
        form_html = form_files_paths.html
        items = []
        with open(form_html, "r") as f:
            line = f.read().strip()
            fields = line.split("[")
            for field in fields:
                if "]" in field:
                    items.append(field.split("]")[0])
        # Remove elements from 'over_fields' that contain any of the ignored fields
        required_fields = [item for item in items if "*" in item]
        required_fields = [item.split(" ")[1] for item in required_fields]
        items = [
            field
            for field in items
            if not any(ignored_field in field for ignored_field in ignored_fields)
        ]
        items = [item.split(" ")[1] for item in items]
        return FormFieldsDto(
            all_fields=items,
            required_fields=required_fields,
        )

    @staticmethod
    def get_submited_fields(form_files_paths: FormFilesDto) -> list[str]:
        form_mail = form_files_paths.mail
        fields = []
        with open(form_mail, "r") as f:
            line = f.read().strip()
            fields = line.split("[")
            items = []
            response = []
            for field in fields:
                if "]" in field:
                    items.append(field.split("]")[0])
            for item in items:
                if not item.startswith("_"):
                    response.append(item)
        return response

    @staticmethod
    def get_random_fields() -> list[RandomFieldDto]:
        file_name = "random_fields.csv"
        script_dir_path = WPPaths.get_script_dir_path()
        file_path = Path(f"{script_dir_path}/contact_forms/{file_name}")
        with open(file_path, "r") as f:
            lines = f.readlines()
            result = []
            # print each line
            for line in lines:
                # remove the newline character
                line = line.replace("\n", "")
                fields = line.split(",")
                result.append(RandomFieldDto(name=fields[0], value=fields[1:]))
        return result

    @staticmethod
    def check_random_fields(
        all_fields: list[str],
        random_fields: list[RandomFieldDto],
        submited_fields: list[str],
    ) -> bool:
        random_fields_names = [field.name for field in random_fields]
        submited_fields.sort()
        random_fields_names.sort()
        all_fields.sort()
        # get difference between all_fields and random_fields
        all_fields_random = set(all_fields) - set(random_fields_names)
        # get difference between all_fields and submited_fields
        all_fields_submited = set(all_fields) - set(submited_fields)
        # get difference between submited_fields and all_fields
        submited_fields_all = set(submited_fields) - set(all_fields)

        if len(all_fields_random) > 0:
            print("[red] Html fields not in random")
            [print(f"[red]{field}") for field in all_fields_random]
            return False
        elif len(all_fields_submited) > 0:
            print("[red] Html fields not in submited")
            [print(f"[red]{field}") for field in all_fields_submited]
            return False
        elif len(submited_fields_all) > 0:
            print("[red] Submited fields not in html")
            [print(f"[red]{field}") for field in submited_fields_all]
            return False
        else:
            return True

    @staticmethod
    def show_contact_form_fields(
        all_fields: list[str], required_fields: list[str], submited_fields: list[str]
    ) -> None:
        # sort submited_fields by required_fields
        sorted_submited_fields = []
        for field in all_fields:
            if field in submited_fields:
                sorted_submited_fields.append(field)
        sorted_submited_fields += [
            field for field in submited_fields if field not in all_fields
        ]

        table_title = "Contact Form Fields"
        table_columns = ["All fields", "Required fields", "Submitted fields"]
        table_rows = []
        for field in sorted_submited_fields:
            if field in required_fields:
                table_rows.append([field, field, field])
            else:
                table_rows.append([field, "[red]No required", field])
        Menu.display(
            table_title, table_columns, table_rows, row_styles={"color": "blue"}
        )
