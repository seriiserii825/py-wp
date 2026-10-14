import csv
import os

from classes.acf.enum.EFieldType import EFieldType
from classes.acf.field.dto.FieldDTO import FieldDTO
from classes.acf.field.factories.FieldTemplateFactory import FieldTemplateFactory
from classes.utils.Generate import Generate
from classes.utils.WPPaths import WPPaths


class PredefinedFieldCreator:
    # bundled with py-wp itself (same convention as PathKey.LIST_CSV), not the
    # theme directory the tool is currently run against
    TYPE_CSV_RELATIVE_PATH = "acf/predefined-acf-fields.csv"
    DEFAULT_WIDTH = 100

    def __init__(self, type_csv_path: str | None = None):
        self.type_csv_path = type_csv_path or str(
            WPPaths.get_script_dir_path() / self.TYPE_CSV_RELATIVE_PATH
        )

    def load_type_map(self) -> dict[str, str]:
        if not os.path.exists(self.type_csv_path):
            raise ValueError(f"Type dictionary not found: {self.type_csv_path}")
        with open(self.type_csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            return {row["title"]: row["type"] for row in reader if row.get("title")}

    def build(self, group_slug: str, field_slugs: list[str]) -> list[dict]:
        group_slug = group_slug.strip()
        field_slugs = [s.strip() for s in field_slugs if s.strip()]
        if not group_slug:
            raise ValueError("Group slug is required.")
        if not field_slugs:
            raise ValueError("At least one field slug is required.")

        type_map = self.load_type_map()
        missing = [slug for slug in field_slugs if slug not in type_map]
        if missing:
            raise ValueError(
                f"Unknown field slug(s): {', '.join(missing)}. "
                f"Add them to {self.type_csv_path} first."
            )

        group_label = self._slug_to_label(group_slug)
        tab_field = FieldTemplateFactory.create(
            FieldDTO(
                key=Generate.get_field_id(),
                label=group_label,
                name="",
                type=EFieldType.TAB,
                width=self.DEFAULT_WIDTH,
            )
        )
        group_field = FieldTemplateFactory.create(
            FieldDTO(
                key=Generate.get_field_id(),
                label=group_label,
                name=self._label_to_name(group_label),
                type=EFieldType.GROUP,
                layout="block",
                width=self.DEFAULT_WIDTH,
            )
        )
        group_field["sub_fields"] = [
            self._build_field(slug, type_map[slug]) for slug in field_slugs
        ]

        return [tab_field, group_field]

    def _build_field(self, slug: str, type_value: str) -> dict:
        label = self._slug_to_label(slug)
        return FieldTemplateFactory.create(
            FieldDTO(
                key=Generate.get_field_id(),
                label=label,
                name=self._label_to_name(label),
                type=EFieldType(type_value),
                width=self.DEFAULT_WIDTH,
            )
        )

    @staticmethod
    def _slug_to_label(slug: str) -> str:
        return slug.replace("-", " ").title()

    @staticmethod
    def _label_to_name(label: str) -> str:
        return label.replace(" ", "_").lower()
