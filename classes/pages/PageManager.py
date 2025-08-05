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
