import csv
import os
import re
from dataclasses import dataclass

from classes.acf.enum.EFieldType import EFieldType
from classes.acf.field.dto.FieldDTO import FieldDTO
from classes.acf.field.factories.FieldTemplateFactory import FieldTemplateFactory
from classes.utils.Generate import Generate
from classes.utils.WPPaths import WPPaths


@dataclass
class _FieldSpec:
    slug: str
    width: int
    type_shortcut: str | None = None  # None => repeater container
    sub_specs: list["_FieldSpec"] | None = None  # None = plain field, else = repeater


class PredefinedFieldCreator:
    # bundled with py-wp itself (same convention as PathKey.LIST_CSV), not the
    # theme directory the tool is currently run against
    TYPE_CSV_RELATIVE_PATH = "acf/predefined-acf-fields.csv"
    DEFAULT_WIDTH = 100

    # name/type-shortcut, optional /width, e.g. title/t/40
    PLAIN_RE = re.compile(
        r"^(?P<slug>[a-zA-Z0-9_-]+)/(?P<type>[a-zA-Z0-9_-]+)"
        r"(?:/(?P<width>\d+))?$"
    )
    # repeater: name, optional /width, [sub1,sub2,...]
    REPEATER_RE = re.compile(
        r"^(?P<slug>[a-zA-Z0-9_-]+)(?:/(?P<width>\d+))?\[(?P<sub_fields>.+)\]$"
    )

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

    @staticmethod
    def split_top_level(raw: str) -> list[str]:
        """Split on commas, ignoring commas nested inside [...] (repeater fields)."""
        tokens = []
        depth = 0
        current: list[str] = []
        for ch in raw:
            if ch == "[":
                depth += 1
                current.append(ch)
            elif ch == "]":
                depth -= 1
                current.append(ch)
            elif ch == "," and depth == 0:
                tokens.append("".join(current))
                current = []
            else:
                current.append(ch)
        tokens.append("".join(current))
        return [t.strip() for t in tokens if t.strip()]

    def build(self, group_slug: str, field_specs: list[str]) -> list[dict]:
        group_slug = group_slug.strip()
        field_specs = [s.strip() for s in field_specs if s.strip()]
        if not group_slug:
            raise ValueError("Group slug is required.")
        if not field_specs:
            raise ValueError("At least one field spec is required.")

        parsed_specs = [self._parse_field_spec(spec) for spec in field_specs]

        type_map = self.load_type_map()
        missing = self._collect_missing_shortcuts(parsed_specs, type_map)
        if missing:
            raise ValueError(
                f"Unknown type shortcut(s): {', '.join(missing)}. "
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
            self._build_from_spec(spec, type_map) for spec in parsed_specs
        ]

        return [tab_field, group_field]

    def _parse_field_spec(self, spec: str) -> _FieldSpec:
        repeater_match = self.REPEATER_RE.match(spec)
        if repeater_match:
            slug = repeater_match.group("slug")
            width = (
                int(repeater_match.group("width"))
                if repeater_match.group("width")
                else self.DEFAULT_WIDTH
            )
            sub_specs = [
                self._parse_field_spec(s)
                for s in self.split_top_level(repeater_match.group("sub_fields"))
            ]
            if not sub_specs:
                raise ValueError(
                    f"Repeater '{slug}' must contain at least one field, "
                    f"e.g. {slug}[title/t,text/wy]."
                )
            return _FieldSpec(slug=slug, width=width, sub_specs=sub_specs)

        plain_match = self.PLAIN_RE.match(spec)
        if plain_match:
            width = (
                int(plain_match.group("width"))
                if plain_match.group("width")
                else self.DEFAULT_WIDTH
            )
            return _FieldSpec(
                slug=plain_match.group("slug"),
                width=width,
                type_shortcut=plain_match.group("type"),
            )

        raise ValueError(
            f"Invalid field spec: '{spec}'. Use name/type or name/type/width, "
            "or a repeater name[sub1/type,sub2/type/width]."
        )

    def _collect_missing_shortcuts(
        self, specs: list[_FieldSpec], type_map: dict[str, str]
    ) -> list[str]:
        missing: list[str] = []
        for spec in specs:
            if spec.sub_specs is None:
                if spec.type_shortcut not in type_map:
                    missing.append(f"{spec.slug}/{spec.type_shortcut}")
            else:
                missing.extend(
                    self._collect_missing_shortcuts(spec.sub_specs, type_map)
                )
        return missing

    def _build_from_spec(self, spec: _FieldSpec, type_map: dict[str, str]) -> dict:
        if spec.sub_specs is None:
            assert spec.type_shortcut is not None
            return self._build_field(
                spec.slug, type_map[spec.type_shortcut], spec.width
            )

        label = self._slug_to_label(spec.slug)
        repeater_field = FieldTemplateFactory.create(
            FieldDTO(
                key=Generate.get_field_id(),
                label=label,
                name=self._label_to_name(label),
                type=EFieldType.REPEATER,
                layout="block",
                width=spec.width,
            )
        )
        repeater_field["sub_fields"] = [
            self._build_from_spec(sub, type_map) for sub in spec.sub_specs
        ]
        return repeater_field

    def _build_field(self, slug: str, type_value: str, width: int) -> dict:
        label = self._slug_to_label(slug)
        return FieldTemplateFactory.create(
            FieldDTO(
                key=Generate.get_field_id(),
                label=label,
                name=self._label_to_name(label),
                type=EFieldType(type_value),
                width=width,
            )
        )

    @staticmethod
    def _slug_to_label(slug: str) -> str:
        return slug.replace("-", " ").title()

    @staticmethod
    def _label_to_name(label: str) -> str:
        return label.replace(" ", "_").lower()
