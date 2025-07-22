import json
import os
from typing import Any, Optional

from classes.acf.AcfTransfer import AcfTransfer
from classes.acf.section.CreateSection import CreateSection
from classes.acf.section.SectionMenu import SectionMenu
from classes.exception.NewSectionException import NewSectionException
from classes.utils.InputValidator import InputValidator
from classes.utils.Print import Print


class EditSection:
    @staticmethod
    def choose_file() -> str:
        files = os.listdir("acf")
        if not files:
            raise NewSectionException("No ACF files found to edit.")
        Print.info("Choose a file to edit:")
        for i, f in enumerate(files):
            print(f"{i}. {f}")
        index = InputValidator.get_int("Enter file index: ")
        return files[index]

    @staticmethod
    def show_section_info():
        file_name = EditSection.choose_file()
        file_path = f"acf/{file_name}"

        if not os.path.exists(file_path):
            Print.error(f"File '{file_name}' does not exist.")
            return

        with open(file_path, "r") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                Print.error("Invalid JSON in file.")
                return

        section = data[0] if isinstance(data, list) and data else {}
        Print.info(f"Section: {file_name}")
        print("=" * 40)
        print(f"Title: {section.get('title')}")
        print(f"Key: {section.get('key')}")
        print(f"Location: {json.dumps(section.get('location'), indent=4)}")
        print(f"Fields count: {len(section.get('fields', []))}")
        print("First 3 fields (if any):")
        for i, field in enumerate(section.get("fields", [])[:3]):
            print(f"  {i + 1}. {field.get('label')} ({field.get('name')})")
        print("=" * 40)

    @staticmethod
    def edit_location():
        file_name = EditSection.choose_file()
        file_path = f"acf/{file_name}"

        with open(file_path, "r") as f:
            data = json.load(f)

        section = data[0]
        locations: list[list[dict[str, Any]]] = section.get("location", [])
        section["key"]
        section["title"]

        while True:
            Print.info("Current Locations:")
            for i, group in enumerate(locations):
                cond = group[0]
                print(f"{i}. {cond['param']} == {cond['value']}")

            menu = [
                "Replace all locations",
                "Append new location",
                "Remove a location",
                "Edit a location",
                "Save and Exit",
            ]
            SectionMenu.display(
                "Edit Location",
                ["Index", "Action"],
                [[str(i), m] for i, m in enumerate(menu)],
            )
            choice = SectionMenu.choose_option()

            if choice == 0:
                new_cond = EditSection._prompt_location()
                if new_cond:
                    locations = [[new_cond]]
            elif choice == 1:
                new_cond = EditSection._prompt_location()
                if new_cond:
                    locations.append([new_cond])
            elif choice == 2:
                index = InputValidator.get_int("Enter index to remove: ")
                if 0 <= index < len(locations):
                    del locations[index]
            elif choice == 3:
                index = InputValidator.get_int("Enter index to edit: ")
                if 0 <= index < len(locations):
                    new_cond = EditSection._prompt_location()
                    if new_cond:
                        locations[index] = [new_cond]
            elif choice == 4:
                break

        section["location"] = locations
        with open(file_path, "w") as f:
            json.dump([section], f, indent=4)
        Print.success(f"File '{file_name}' updated.")
        want_to_import = InputValidator.get_bool(
            "Do you want to import the updated ACF data? (y/n): "
        )
        if want_to_import:
            AcfTransfer.wp_import()
            Print.success("ACF data imported successfully.")

    @staticmethod
    def _prompt_location() -> Optional[dict[str, Any]]:
        choice = CreateSection.choose_type()
        if choice == 1:
            page = CreateSection.select_page()
            return {
                "param": "page",
                "operator": "==",
                "value": page.ID,
            }
        elif choice == 2:
            post_type = CreateSection._select_custom_post_type()
            return {
                "param": "post_type",
                "operator": "==",
                "value": post_type,
            }
        elif choice == 3:
            taxonomy = CreateSection._select_taxonomy()
            return {
                "param": "taxonomy",
                "operator": "==",
                "value": taxonomy,
            }
        return None
