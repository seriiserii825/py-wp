from pathlib import Path
from classes.utils.Command import Command
from classes.utils.Select import Select
from classes.utils.WPPaths import WPPaths
from dto.ContactFormDto import ContactFormDto


class ContactFormFetcher:
    def __init__(self, wp_paths: WPPaths, command: Command, selector: Select):
        self.wp_paths = wp_paths
        self.command = command
        self.selector = selector

    def fetch(self) -> ContactFormDto:
        script_dir_path = self.wp_paths.get_script_dir_path()
        theme_path = self.wp_paths.get_theme_path()
        theme_name = theme_path.name
        csv_file_path = Path(f"{script_dir_path}/contact_forms/{theme_name}.csv")
        csv_file_path.parent.mkdir(parents=True, exist_ok=True)

        cmd = (
            f"wp post list --post_type=wpcf7_contact_form --format=csv "
            f"--allow-root > {csv_file_path}"
        )
        self.command.run(cmd)

        lines = csv_file_path.read_text().splitlines()
        result = [f"{line.split(',')[1]}-{line.split(',')[0]}" for line in lines[1:]]
        selected = self.selector.select_one(result)

        form_name, form_id = self._normalize(selected)
        form_folder_path = Path(f"{script_dir_path}/{theme_name}/{form_name}-{form_id}")
        form_folder_path.mkdir(parents=True, exist_ok=True)

        return ContactFormDto(
            id=form_id,
            title=form_name,
            csv_file_path=str(csv_file_path),
            form_folder_path=str(form_folder_path),
        )

    def _normalize(self, selected: str) -> tuple[str, str]:
        form_name = selected.split("-")[0].lower()
        form_id = selected.split("-")[1]
        for char in ' ()/\\:*?"<>':
            form_name = form_name.replace(char, "-")
        return form_name, form_id
