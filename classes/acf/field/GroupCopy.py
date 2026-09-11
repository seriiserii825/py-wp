import pyperclip

from classes.acf.field.FieldMover import FieldMover
from classes.utils.Notification import Notification


class GroupCopy:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.mover = FieldMover()

    def copy_to_clipboard(self, fields: list, index_path_str: str):
        index_path = self.mover.parse_index_path(index_path_str)
        field = self._get_nested_field(fields, index_path)

        if field is None or field.get("type") not in ["group", "repeater"]:
            raise ValueError("Selected field must be a group or repeater.")

        php_lines: list = []
        var_name = field["name"]
        var_expr = f"${var_name}"
        php_lines.append(f"{var_expr} = get_field('{var_name}');")
        self._generate_sub_fields(field, source_expr=var_expr, indent=0, output=php_lines, repeater_depth=0)

        php_code = "\n".join(php_lines)
        pyperclip.copy(php_code)
        nt = Notification(
            title="Group copied to clipboard",
            message="PHP code for the group has been copied.",
        )
        nt.notify()

    def _generate_sub_fields(
        self, field: dict, source_expr: str, indent: int, output: list, repeater_depth: int
    ):
        field_type = field.get("type")
        sub_fields = field.get("sub_fields", [])
        prefix = "    " * indent

        if field_type == "repeater":
            repeater_depth += 1
            # Unique loop variable per nesting depth so nested repeaters don't shadow each other.
            item_var = "$item" if repeater_depth == 1 else f"$item{repeater_depth}"
            output.append(f"{prefix}foreach ({source_expr} as {item_var}) {{")
            for sub in sub_fields:
                self._emit_field(sub, item_var, indent + 1, output, repeater_depth)
            output.append(f"{prefix}}}")
        else:
            for sub in sub_fields:
                self._emit_field(sub, source_expr, indent, output, repeater_depth)

    def _emit_field(
        self, field: dict, source_expr: str, indent: int, output: list, repeater_depth: int
    ):
        name = field.get("name")
        if not name:
            return

        prefix = "    " * indent
        var_expr = f"${name}"
        output.append(f"{prefix}{var_expr} = {source_expr}['{name}'];")

        if field.get("type") in ("group", "repeater"):
            self._generate_sub_fields(field, var_expr, indent, output, repeater_depth)

    def _get_nested_field(self, fields: list, index_path: list):
        current = fields
        for depth, i in enumerate(index_path):
            i = int(i)
            if not (0 <= i < len(current)):
                raise IndexError(f"Index {i} is out of range at depth {depth}.")
            field = current[i]
            if depth < len(index_path) - 1:
                current = field.get("sub_fields", [])
            else:
                return field
