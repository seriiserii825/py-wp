from pathlib import Path

from classes.contact_form.ContactFormFetcher import ContactFormFetcher
from classes.contact_form.ContactFormFileService import ContactFormFileService
from classes.contact_form.HoneypotChecker import HoneypotChecker
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
        cf = ContactFormFetcher(
            wp_paths=WPPaths(),
            command=Command(),
            selector=Select(),
        )
        return cf.fetch()

    @staticmethod
    def form_to_files(form: ContactFormDto) -> FormFilesDto:
        cf = ContactFormFileService(
            command=Command(),
        )
        return cf.extract_form_files(form)

    @staticmethod
    def check_honeypot(form_files_paths: FormFilesDto) -> None:
        hc = HoneypotChecker()
        hc.check(form_files_paths.html)

    @staticmethod
    def get_required_fields(form_files_paths: FormFilesDto) -> FormFieldsDto:
        fields = []
        ignored_fields = ["timecheck_enabled",
                          "honeypot", "acceptance", "submit"]
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
            table_title, table_columns, table_rows, row_styles={
                "color": "blue"}
        )

    @staticmethod
    def show_contact_form_files(form_files_paths: FormFilesDto) -> None:
        form_html = form_files_paths.html
        form_mail = form_files_paths.mail
        Command.run(f"bat {form_html}")
        Command.run(f"bat {form_mail}")

    @classmethod
    def show_random_fields(cls) -> None:
        random_fields = cls.get_random_fields()
        random_fields = sorted(random_fields, key=lambda k: k.name)
        table_title = "Random Fields"
        table_columns = ["Field", "Values"]
        table_rows = []
        for random_field in random_fields:
            values = ", ".join(random_field.value)
            table_rows.append([random_field.name, values])
        Menu.display(
            table_title, table_columns, table_rows, row_styles={
                "color": "blue"}
        )

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
