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

        php_lines = []
        self._generate_php(field, var_name=field["name"], indent=0, output=php_lines)

        php_code = "\n".join(php_lines)
        pyperclip.copy(php_code)
        nt = Notification(
            title="Group copied to clipboard",
            message="PHP code for the group has been copied.",
        )
        nt.notify()

    def _generate_php(
        self, field: dict, var_name: str, indent: int, output: list, parent_chain=None
    ):
        parent_chain = parent_chain or []

        field_type = field.get("type")
        sub_fields = field.get("sub_fields", [])
        prefix = "    " * indent

        if field_type == "group":
            chain = parent_chain + [var_name]
            var_full = "$" + "_".join(chain)
            output.append(f"{prefix}{var_full} = get_field('{var_name}');")
            for sub in sub_fields:
                sub_name = sub.get("name")
                if sub_name:
                    self._generate_php(
                        sub,
                        var_name=sub_name,
                        indent=indent,
                        output=output,
                        parent_chain=chain,
                    )

        elif field_type == "repeater":
            chain = parent_chain + [var_name]
            var_full = "$" + "_".join(chain)
            output.append(f"{prefix}{var_full} = get_field('{var_name}');")
            for sub in sub_fields:
                sub_name = sub.get("name")
                if sub_name:
                    output.append(f"{prefix}        ${sub_name} = $item['{sub_name}'];")

        else:
            # Simple field inside a group
            if parent_chain:
                chain = "$" + "_".join(parent_chain)
                output.append(f"{prefix}${var_name} = {chain}['{var_name}'];")

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
