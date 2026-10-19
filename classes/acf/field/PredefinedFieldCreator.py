import csv
import os
from dataclasses import dataclass

from classes.acf.enum.EFieldType import EFieldType
from classes.acf.field.dto.FieldDTO import FieldDTO
from classes.acf.field.factories.FieldTemplateFactory import FieldTemplateFactory
from classes.utils.Generate import Generate
from classes.utils.WPPaths import WPPaths


@dataclass
class _FieldSpec:
    label: str
    width: int
    type_shortcut: str | None = None  # None => repeater container
    sub_specs: list["_FieldSpec"] | None = None  # None = plain field, else = repeater


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

    @staticmethod
    def split_top_level(raw: str) -> list[str]:
        """Split on '/', ignoring slashes nested inside [...] (repeater fields)."""
        tokens = []
        depth = 0
        current: list[str] = []
        for ch in raw:
            if ch == "[":
                depth += 1
            elif ch == "]":
                depth -= 1
                if depth < 0:
                    raise ValueError("Unbalanced ']'.")
            elif ch == "/" and depth == 0:
                tokens.append("".join(current).strip())
                current = []
                continue
            current.append(ch)
        if depth != 0:
            raise ValueError("Unbalanced '['.")
        tokens.append("".join(current).strip())
        if any(not t for t in tokens):
            raise ValueError("Empty part (check for '//' or a leading/trailing '/').")
        return tokens

    def parse(self, raw: str) -> tuple[str, list[_FieldSpec]]:
        """Group/Label/type[/width]/Repeater[Label/type[/width]...][/width]...
        e.g. Info/Title/t/30/Items[Image/i/Subtitle/t]/50."""
        tokens = self.split_top_level(raw)
        if len(tokens) < 2:
            raise ValueError("Enter a group label and at least one field (label/type).")
        group_label = self._validate_label(tokens[0])
        return group_label, self._parse_specs(tokens[1:])

    def parse_fields(self, raw: str) -> list[_FieldSpec]:
        """Same as parse() but without the leading group label:
        Label/type[/width]/Repeater[...][/width]..."""
        return self._parse_specs(self.split_top_level(raw))

    def _parse_specs(self, tokens: list[str]) -> list[_FieldSpec]:
        specs: list[_FieldSpec] = []
        i = 0
        while i < len(tokens):
            token = tokens[i]
            i += 1
            if "[" in token:
                if not token.endswith("]"):
                    raise ValueError(f"Invalid repeater '{token}', use Label[...].")
                label, inner = token[:-1].split("[", 1)
                sub_specs = self._parse_specs(self.split_top_level(inner))
                spec = _FieldSpec(
                    label=self._validate_label(label),
                    width=self.DEFAULT_WIDTH,
                    sub_specs=sub_specs,
                )
            else:
                if i >= len(tokens):
                    raise ValueError(f"Field '{token}' has no type, e.g. {token}/t.")
                spec = _FieldSpec(
                    label=self._validate_label(token),
                    width=self.DEFAULT_WIDTH,
                    type_shortcut=tokens[i],
                )
                i += 1
            if i < len(tokens) and tokens[i].isdigit():
                spec.width = int(tokens[i])
                i += 1
            specs.append(spec)
        if not specs:
            raise ValueError("Repeater must contain at least one field, e.g. Items[Title/t].")
        return specs

    @staticmethod
    def _validate_label(label: str) -> str:
        label = label.strip()
        if not label:
            raise ValueError("Label is empty.")
        if label.isdigit():
            raise ValueError(f"Label '{label}' must be text, not a number.")
        if "[" in label or "]" in label:
            raise ValueError(f"Invalid label '{label}'.")
        return label[0].upper() + label[1:]

    def build(self, group_label: str, specs: list[_FieldSpec]) -> list[dict]:
        sub_fields = self.build_fields(specs)

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
        group_field["sub_fields"] = sub_fields

        return [tab_field, group_field]

    def build_fields(self, specs: list[_FieldSpec]) -> list[dict]:
        """Fields only, without the Tab + Group wrapper."""
        type_map = self.load_type_map()
        missing = self._collect_missing_shortcuts(specs, type_map)
        if missing:
            raise ValueError(
                f"Unknown type shortcut(s): {', '.join(missing)}. "
                f"Add them to {self.type_csv_path} first."
            )
        return [self._build_from_spec(spec, type_map) for spec in specs]

    def _collect_missing_shortcuts(
        self, specs: list[_FieldSpec], type_map: dict[str, str]
    ) -> list[str]:
        missing: list[str] = []
        for spec in specs:
            if spec.sub_specs is None:
                if spec.type_shortcut not in type_map:
                    missing.append(f"{spec.label}/{spec.type_shortcut}")
            else:
                missing.extend(
                    self._collect_missing_shortcuts(spec.sub_specs, type_map)
                )
        return missing

    def _build_from_spec(self, spec: _FieldSpec, type_map: dict[str, str]) -> dict:
        if spec.sub_specs is None:
            assert spec.type_shortcut is not None
            return self._build_field(
                spec.label, type_map[spec.type_shortcut], spec.width
            )

        label = spec.label
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

    def _build_field(self, label: str, type_value: str, width: int) -> dict:
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
    def _label_to_name(label: str) -> str:
        return label.replace(" ", "_").lower()
