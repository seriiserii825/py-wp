import re
import shlex

from classes.utils.Command import Command


class PageManager:
    @staticmethod
    def create(title: str):
        Command.run(
            f"wp post create --post_type=page "
            f"--post_status=publish --post_title='{title}'"
        )

    @classmethod
    def create_many(cls, titles: list[str]):
        for title in titles:
            cls.create(title.strip())

    @staticmethod
    def delete(page_id: int):
        Command.run(f"wp post delete {page_id} --force")

    @staticmethod
    def slugify(title: str) -> str:
        return re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")

    @staticmethod
    def rename(page_id: int, title: str, slug: str):
        Command.run(
            f"wp post update {page_id} "
            f"--post_title={shlex.quote(title)} "
            f"--post_name={shlex.quote(slug)}"
        )

    @staticmethod
    def get_templates() -> dict[str, str]:
        raw = Command.run_json(
            "wp eval 'echo json_encode(get_page_templates());'"
        )
        templates: dict[str, str] = {"Default template": "default"}
        templates.update(raw)
        return templates

    @staticmethod
    def change_template(page_id: int, template: str):
        Command.run(
            f"wp post update {page_id} --page_template={shlex.quote(template)}"
        )
