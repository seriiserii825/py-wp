from pathlib import Path

from classes.contact_form.ContactFormFetcher import ContactFormFetcher
from classes.contact_form.ContactFormFileService import ContactFormFileService
from classes.contact_form.FieldParserService import FieldParserService
from classes.contact_form.FieldValidatorService import FieldValidatorService
from classes.contact_form.FormFieldDisplayer import FormFieldDisplayer
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
        fps = FieldParserService()
        return fps.get_required_fields(form_files_paths.html)

    @staticmethod
    def get_submited_fields(form_files_paths: FormFilesDto) -> list[str]:
        fps = FieldParserService()
        return fps.get_submitted_fields(form_files_paths.mail)

    @staticmethod
    def check_random_fields(
        all_fields: list[str],
        random_fields: list[RandomFieldDto],
        submited_fields: list[str],
    ) -> bool:
        fvs = FieldValidatorService()
        return fvs.validate(
            all_fields=all_fields,
            random_fields=random_fields,
            submitted_fields=submited_fields,
        )

    @staticmethod
    def show_contact_form_fields(
        all_fields: list[str], required_fields: list[str], submited_fields: list[str]
    ) -> None:
        ffd = FormFieldDisplayer()
        ffd.show(
            all_fields=all_fields,
            required_fields=required_fields,
            submitted_fields=submited_fields,
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
