from classes.utils.Print import Print


class HoneypotChecker:
    def check(self, form_html_path: str) -> None:
        with open(form_html_path, "r") as f:
            content = f.read().strip()
        fields = [field.split("]")[0] for field in content.split("[") if "]" in field]
        honeypot = [f for f in fields if "honeypot" in f]
        if honeypot:
            Print.info(f"Honeypot field found: [green]{honeypot[0]}[/green]")
        else:
            Print.error("Honeypot field not found.")
