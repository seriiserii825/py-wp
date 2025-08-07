from dto.FormFieldsDto import FormFieldsDto


class FieldParserService:
    def get_required_fields(self, html_path: str) -> FormFieldsDto:
        ignored = ["timecheck_enabled", "honeypot", "acceptance", "submit"]
        with open(html_path, "r") as f:
            content = f.read().strip()
        raw_fields = [f.split("]")[0] for f in content.split("[") if "]" in f]

        required = [f.split(" ")[1] for f in raw_fields if "*" in f]
        all_fields = [
            f.split(" ")[1] for f in raw_fields
            if not any(x in f for x in ignored) and " " in f
        ]

        return FormFieldsDto(all_fields=all_fields, required_fields=required)

    def get_submitted_fields(self, mail_path: str) -> list[str]:
        with open(mail_path, "r") as f:
            content = f.read().strip()
        fields = [f.split("]")[0] for f in content.split("[") if "]" in f]
        return [f for f in fields if not f.startswith("_")]
