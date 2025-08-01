import json
import os
from typing import Any, List

from classes.acf.section.SectionMenu import SectionMenu
from classes.data.WpData import WpData
from classes.exception.NewSectionException import NewSectionException
from classes.utils.Generate import Generate
from classes.utils.InputValidator import InputValidator
from classes.utils.Menu import Menu
from classes.utils.Print import Print
from dto.SectionDto import SectionDTO


class CreateSection:
    section_name: str = ""
    file_name: str = ""
    file_path: str = ""

    @classmethod
    def add_name_and_file_path(cls):
        name = InputValidator.get_string("Enter section name: ")
        cls.section_name = name
        cls._set_file_name(name)
        cls._set_file_path(cls.file_name)

    @classmethod
    def _set_file_name(cls, section_name: str) -> None:
        cls.file_name = section_name.replace(" ", "-").lower() + ".json"

    @classmethod
    def _set_file_path(cls, file_name: str):
        cls.file_path = f"acf/{file_name}"
        if not os.path.exists("acf"):
            raise NewSectionException("The 'acf' directory does not exist.")
        if os.path.exists(cls.file_path):
            raise NewSectionException(
                f"The file '{file_name}' already exists in the 'acf' directory."
            )

    @staticmethod
    def choose_type() -> int:
        rows = [
            "Page",
            "Custom Post Type",
            "Taxonomy",
            "Options Page",
            "Exit",
        ]
        choice = Menu.select_with_fzf(rows)
        print(f"choose_type: {choice}")
        return choice

    @classmethod
    def new_acf_page(cls):
        page = cls.select_page()
        cls._create_file(page_id=page.ID)

    @staticmethod
    def select_page() -> SectionDTO:
        row_pages: List[dict[str, Any]] = WpData.get_wp_pages()
        pages: List[SectionDTO] = [
            SectionDTO(
                ID=row["ID"],
                post_title=row["post_title"],
                post_name=row["post_name"],
                post_date=row["post_date"],
                post_status=row["post_status"],
            )
            for row in row_pages
        ]
        Print.info(f"pages: {pages}")

        rows = [i.post_title for i in pages]
        index = Menu.select_with_fzf(rows)
        print(f"index: {index}")
        print(f"pages[index]: {pages[index]}")

        return pages[index]

    @classmethod
    def new_acf_custom_post_type(cls):
        post_type = cls._select_custom_post_type()
        cls._create_file(post_type=post_type)

    @staticmethod
    def _select_custom_post_type() -> str:
        row_post_types: List[str] = WpData.get_wp_posts()
        columns = ["Index", "Post Type"]
        rows = [[str(row_post_types.index(i)), i] for i in row_post_types]
        SectionMenu.display("New Section", columns, rows)
        index = SectionMenu.choose_option()
        post_type = row_post_types[index]
        return post_type

    @classmethod
    def new_acf_taxonomy(cls):
        taxonomy = cls._select_taxonomy()
        cls._create_file(taxonomy=taxonomy)

    @staticmethod
    def _select_taxonomy() -> str:
        taxonomies: List[str] = WpData.get_wp_taxonomies()
        columns = ["Index", "Taxonomy"]
        rows = [[str(taxonomies.index(i)), i] for i in taxonomies]
        SectionMenu.display("New Section", columns, rows)
        index = SectionMenu.choose_option()
        taxonomy = taxonomies[index]
        return taxonomy

    @classmethod
    def new_acf_options_page(cls):
        options_pages: List[str] = WpData.get_acf_options_pages()
        print(f"options_pages:: {options_pages:}")
        if not options_pages:
            Print.error("No ACF options pages found.")
            return

        columns = ["Index", "Options Page"]
        rows = [[str(options_pages.index(i)), i] for i in options_pages]
        SectionMenu.display("New Section", columns, rows)
        index = SectionMenu.choose_option()
        options_page = options_pages[index]

        cls._create_file(post_type="options_page", taxonomy=options_page)

    @classmethod
    def _create_file(cls, page_id=0, post_type="", taxonomy="", options_page=""):
        group_id = Generate.get_group_id()
        os.system(f"touch {cls.file_path}")
        data = cls.build_acf_data(
            group_id, cls.section_name, page_id, post_type, taxonomy, options_page
        )
        with open(cls.file_path, "w") as file:
            json.dump([data], file, indent=4)

    @classmethod
    def build_acf_data(
        cls,
        group_id: str,
        section_name: str,
        page_id: int = 0,
        post_type: str = "",
        taxonomy: str = "",
        options_page: str = "",
    ) -> dict:
        new_data = {
            "ID": False,
            "key": group_id,
            "title": section_name,
            "fields": [],
            "menu_order": 0,
            "position": "normal",
            "style": "default",
            "label_placement": "top",
            "instruction_placement": "label",
            "hide_on_screen": "",
            "active": True,
            "description": "",
            "show_in_rest": 0,
            "_valid": True,
        }

        if post_type:
            new_data["location"] = [
                [{"param": "post_type", "operator": "==", "value": post_type}]
            ]
        elif taxonomy:
            new_data["location"] = [
                [{"param": "taxonomy", "operator": "==", "value": taxonomy}]
            ]
        elif page_id:
            new_data["location"] = [
                [{"param": "page", "operator": "==", "value": page_id}]
            ]
        elif options_page:
            new_data["location"] = [
                [{"param": "options_page", "operator": "==", "value": options_page}]
            ]

        return new_data

    @staticmethod
    def show_all_files():
        files = os.listdir("acf")
        if not files:
            Print.info("No ACF files found.")
            return
        Print.info("show_all_files:")
        for file in files:
            print(f"- {file}")
