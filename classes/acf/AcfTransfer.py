import json
from pathlib import Path

from classes.utils.Command import Command
from classes.utils.Print import Print


class AcfTransfer:
    @staticmethod
    def _sort_fields(fields: list) -> list:
        sorted_fields = sorted(fields, key=lambda f: f.get("menu_order", 0))
        for field in sorted_fields:
            for key in ("fields", "sub_fields"):
                if field.get(key):
                    field[key] = AcfTransfer._sort_fields(field[key])
        return sorted_fields

    @staticmethod
    def _sort_acf_json_files():
        for path in Path("acf").glob("*.json"):
            data = json.loads(path.read_text(encoding="utf-8"))
            for group in data:
                if group.get("fields"):
                    group["fields"] = AcfTransfer._sort_fields(group["fields"])
            path.write_text(json.dumps(data, indent=4, ensure_ascii=False), encoding="utf-8")

    @staticmethod
    def wp_export():
        try:
            Command.run_quiet("wp db check")  # check DB connection
            Command.run("rm -rf acf")
            Command.run("wp acf export --all")
            AcfTransfer._sort_acf_json_files()
        except RuntimeError as e:
            Print.error(f"Error during ACF export: {e}")
            exit(1)

    @staticmethod
    def wp_import():
        try:
            Command.run_quiet("wp db check")  # check DB connection
            AcfTransfer._sort_acf_json_files()
            Command.run("wp acf clean")
            Command.run("wp acf import --all")
        except RuntimeError as e:
            Print.error(f"Error during ACF import: {e}")
            exit(1)
