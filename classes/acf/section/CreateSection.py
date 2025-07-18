import json
import os
from typing import Any, List

from classes.acf.section.SectionMenu import SectionMenu
from classes.data.WpData import WpData
from classes.exception.NewSectionException import NewSectionException
from classes.utils.Generate import Generate
from classes.utils.InputValidator import InputValidator
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
        columns = ["Index", "Option"]
        rows = [
            ["1", "Page"],
            ["2", "Custom Post Type"],
            ["3", "Taxonomy"],
            ["4", "Exit"],
        ]
        SectionMenu.display("New Section", columns, rows)
        choice = SectionMenu.choose_option()
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

        columns = ["Index", "ID", "Title"]
        rows = [[str(pages.index(i)), f"{i.ID}", i.post_title] for i in pages]

        SectionMenu.display("New Section", columns, rows)
        index = SectionMenu.choose_option()
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
    def _create_file(cls, page_id: int = 0, post_type: str = "", taxonomy: str = ""):
        group_id = Generate.get_group_id()
        os.system(f"touch {cls.file_path}")
        new_data = {}
        new_data["ID"] = False
        new_data["key"] = group_id
        new_data["title"] = cls.section_name
        new_data["fields"] = []
        if post_type:
            new_data["location"] = [
                [
                    {
                        "param": "post_type",
                        "operator": "==",
                        "value": post_type,
                    }
                ]
            ]
        elif taxonomy:
            new_data["location"] = [
                [
                    {
                        "param": "taxonomy",
                        "operator": "==",
                        "value": taxonomy,
                    }
                ]
            ]
        else:
            new_data["location"] = [
                [
                    {
                        "param": "page",
                        "operator": "==",
                        "value": page_id,
                    }
                ]
            ]
        new_data["menu_order"] = 0
        new_data["position"] = "normal"
        new_data["style"] = "default"
        new_data["label_placement"] = "top"
        new_data["instruction_placement"] = "label"
        new_data["hide_on_screen"] = ""
        new_data["active"] = True
        new_data["description"] = ""
        new_data["show_in_rest"] = 0
        new_data["_valid"] = True

        json_data = json.dumps(new_data, indent=4)
        json_data = f"[{json_data}]\n"  # Wrap in a list for ACF compatibility
        with open(cls.file_path, "w") as file:
            # write
            file.write(json_data)

    @staticmethod
    def show_all_files():
        files = os.listdir("acf")
        if not files:
            Print.info("No ACF files found.")
            return
        Print.info("show_all_files:")
        for file in files:
            print(f"- {file}")
