from typing import Callable

from classes.acf.field.FieldMover import FieldMover


class MultipleFieldEditor:
    """Edits one attribute (label / width / type) of several fields at once
    from a single line: index/value/index/value, e.g. 1.2/My label/2.4/New."""

    LABEL = "label"
    WIDTH = "width"
    TYPE = "type"

    MIN_WIDTH = 20
    MAX_WIDTH = 100
    # changing the type of these would orphan sub_fields / break the layout
    CONTAINER_TYPES = {"tab", "group", "repeater"}

    def __init__(self, mover: FieldMover):
        self.mover = mover

    def parse(
        self,
        raw: str,
        attr: str,
        fields: list,
        type_map: dict[str, str],
    ) -> list[tuple[str, dict, str]]:
        """Validate the whole line; return (index, field, value) for every pair
        or raise ValueError listing every problem found."""
        parts = [p.strip() for p in raw.split("/")]
        if len(parts) < 2 or len(parts) % 2 != 0:
            raise ValueError(
                "Use pairs index/value separated by '/', e.g. 1.2/value/2.4/value."
            )

        validators: dict[str, Callable[[str, dict], str | None]] = {
            self.LABEL: self._validate_label,
            self.WIDTH: self._validate_width,
            self.TYPE: lambda v, f: self._validate_type(v, f, type_map),
        }
        validate = validators[attr]

        errors: list[str] = []
        result: list[tuple[str, dict, str]] = []
        seen: set[str] = set()
        for index, value in zip(parts[::2], parts[1::2]):
            if index in seen:
                errors.append(f"{index}: index given more than once.")
                continue
            seen.add(index)
            field = self._get_field(fields, index)
            if field is None:
                errors.append(f"{index}: field does not exist.")
                continue
            error = validate(value, field)
            if error:
                errors.append(f"{index}: {error}")
                continue
            result.append((index, field, value))

        if errors:
            raise ValueError("\n".join(errors))
        return result

    def apply(
        self, attr: str, field: dict, value: str, type_map: dict[str, str]
    ) -> str:
        """Set the attribute; return the old value for the summary."""
        if attr == self.LABEL:
            old = field.get("label", "")
            field["label"] = value
            # tabs have no name in ACF
            if field.get("type") != "tab":
                field["name"] = self.label_to_name(value)
            return str(old)
        if attr == self.WIDTH:
            wrapper = field.setdefault("wrapper", {})
            old = wrapper.get("width", "")
            wrapper["width"] = int(value)
            return str(old)
        old = field.get("type", "")
        field["type"] = type_map[value]
        return str(old)

    def _get_field(self, fields: list, index: str) -> dict | None:
        try:
            field = self.mover.get_field_by_index(fields, index)
        except (IndexError, KeyError, ValueError, TypeError):
            return None
        return field if isinstance(field, dict) else None

    @staticmethod
    def _validate_label(value: str, field: dict) -> str | None:
        if not value:
            return "label is empty."
        if value.isdigit():
            return f"label '{value}' must be text, not a number."
        return None

    def _validate_width(self, value: str, field: dict) -> str | None:
        if not value.isdigit():
            return f"width '{value}' is not a number."
        if not self.MIN_WIDTH <= int(value) <= self.MAX_WIDTH:
            return (
                f"width {value} out of range "
                f"({self.MIN_WIDTH}-{self.MAX_WIDTH})."
            )
        return None

    def _validate_type(
        self, value: str, field: dict, type_map: dict[str, str]
    ) -> str | None:
        if value not in type_map:
            return (
                f"unknown type '{value}', "
                f"available: {', '.join(type_map)}."
            )
        if field.get("type") in self.CONTAINER_TYPES:
            return f"field is a {field.get('type')}, its type can't be changed."
        return None

    @staticmethod
    def label_to_name(label: str) -> str:
        return label.replace(" ", "_").lower()
