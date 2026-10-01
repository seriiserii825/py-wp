from classes.pages.PageManager import PageManager
from dto.PostDto import PostDto
from py_libs.Command import Command
from py_libs.Menu import Menu
from py_libs.Print import Print
from py_libs.Select import Select


class Post:
    posts: list[PostDto] = []

    @classmethod
    def list_all(cls):
        cls.init_posts()
        headers = ["ID", "Title", "Slug", "Status", "Date"]
        data = [
            [str(p.ID), p.post_title, p.post_name, p.post_status, p.post_date]
            for p in sorted(cls.posts, key=lambda x: x.post_date)
        ]
        Menu.display("List of Posts", headers, data)

    @classmethod
    def init_posts(cls):
        raw_posts = Command.run_json(
            "wp post list --post_type=post --format=json "
            "--fields=ID,post_title,post_name,post_date,post_status"
        )
        cls.posts = [PostDto(**p) for p in raw_posts]

    @classmethod
    def create_one(cls):
        title = input("Enter post title: ").strip()
        if not title:
            Print.error("Title cannot be empty.")
            return
        PageManager.create(title, post_type="post")
        Print.success(f"Post '{title}' created successfully.")

    @classmethod
    def create_many(cls):
        mode = Select.select_fzf_one(
            ["Different titles (separated by |)", "One title x N times"]
        )
        if mode is None:
            Print.error("Nothing selected.")
            return
        if mode.startswith("One title"):
            titles = cls.ask_repeated_title()
        else:
            titles = [
                t.strip()
                for t in input(
                    "Enter post titles (separated by |): ").split("|")
                if t.strip()
            ]
        if not titles:
            Print.error("No titles provided.")
            return
        PageManager.create_many(titles, post_type="post")
        Print.success(f"Created {len(titles)} posts successfully.")

    @staticmethod
    def ask_repeated_title() -> list[str]:
        title = input("Enter post title: ").strip()
        if not title:
            return []
        count = input("How many posts to create: ").strip()
        if not count.isdigit() or int(count) < 1:
            Print.error("Count must be a positive number.")
            return []
        return [title] * int(count)

    @classmethod
    def delete(cls):
        cls.list_all()
        if not cls.posts:
            Print.error("No posts available to delete.")
            return
        selected = cls.select_posts()
        if not selected:
            Print.error("No posts selected for deletion.")
            return
        for post_id in selected:
            PageManager.delete(post_id)
            Print.success(f"Deleted post ID {post_id}")

    @classmethod
    def rename(cls):
        cls.list_all()
        if not cls.posts:
            Print.error("No posts available to rename.")
            return
        selected = Select.select_fzf_one(cls.options())
        if not selected:
            Print.error("No post selected.")
            return
        post_id = int(selected.split("-")[0])
        post = next(p for p in cls.posts if p.ID == post_id)

        title = input(
            f"Enter new title [{post.post_title}]: "
        ).strip() or post.post_title
        default_slug = PageManager.slugify(title)
        slug = input(
            f"Enter new slug [{default_slug}]: "
        ).strip() or default_slug

        PageManager.rename(post_id, title, slug)
        Print.success(
            f"Renamed post ID {post_id} to '{title}' (slug: {slug})")

    @classmethod
    def options(cls) -> list[str]:
        return [f"{p.ID}-{p.post_title}" for p in cls.posts]

    @classmethod
    def select_posts(cls) -> list[int]:
        selected = Select.select_with_fzf(cls.options())
        return [int(item.split("-")[0]) for item in selected]
