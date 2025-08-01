import json
import os
import re

from classes.utils.WPPaths import WPPaths


class WpData:
    @staticmethod
    def get_wp_pages():
        json_pages = os.popen("wp post list --post_type=page --format=json").read()
        data = json.loads(json_pages)
        pages = []
        for page in data:
            page_name = page
            pages.append(page_name)
        return pages

    @staticmethod
    def get_wp_posts():
        json_posts = os.popen(
            "wp post-type list --publicly_queryable=1 --fields=name --format=json"
        ).read()
        data = json.loads(json_posts)
        posts = []
        for post in data:
            post_name = post["name"]
            posts.append(post_name)
        return posts

    @staticmethod
    def get_wp_taxonomies() -> list[str]:
        json_taxonomies = os.popen(
            "wp taxonomy list --fields=name --format=json"
        ).read()
        data = json.loads(json_taxonomies)
        taxonomies = []
        for taxonomy in data:
            taxonomy_name = taxonomy["name"]
            taxonomies.append(taxonomy_name)
        return taxonomies

    @staticmethod
    def get_acf_options_pages() -> list[str]:
        theme_path = WPPaths.get_theme_path()
        acf_file_path = f"{theme_path}/inc/acf.php"

        if not os.path.exists(acf_file_path):
            return []

        # Read the PHP file
        with open(acf_file_path, "r") as file:
            content = file.read()

        pattern = r"'menu_slug'\s*=>\s*'([^']+)'"
        matches = re.findall(pattern, content)

        # Create key-value pairs (key is index-based or slug-based)
        options_pages = [menu_slug for _, menu_slug in enumerate(matches)]

        return options_pages
