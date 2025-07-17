import json
import os


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
