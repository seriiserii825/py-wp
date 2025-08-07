from pathlib import Path

from classes.contact_form.ContactFormFetcher import ContactFormFetcher
from classes.contact_form.ContactFormFileService import ContactFormFileService
from classes.contact_form.FieldParserService import FieldParserService
from classes.contact_form.FieldValidatorService import FieldValidatorService
from classes.contact_form.FormFieldDisplayer import FormFieldDisplayer
from classes.contact_form.FormFileDisplayer import FormFileDisplayer
from classes.contact_form.HoneypotChecker import HoneypotChecker
from classes.contact_form.RandomFieldDisplayer import RandomFieldDisplayer
from classes.contact_form.RandomFieldService import RandomFieldService
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
        ffd = FormFileDisplayer(command=Command())
        ffd.show(
            html_path=form_files_paths.html,
            mail_path=form_files_paths.mail,
        )

    @classmethod
    def show_random_fields(cls) -> None:
        rfd = RandomFieldDisplayer()
        rfd.show(
            random_fields=cls.get_random_fields(),
        )

    @staticmethod
    def get_random_fields() -> list[RandomFieldDto]:
        rfs = RandomFieldService(
            wp_paths=WPPaths(),
        )
        return rfs.get_random_fields()
