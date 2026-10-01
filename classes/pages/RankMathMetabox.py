import json
import shlex

from py_libs.Command import Command
from py_libs.Print import Print
from py_libs.Select import Select


class RankMathMetabox:
    """Show/hide Rank Math metaboxes in the post editor ("Screen Options").

    WordPress stores the unchecked Screen Options boxes per user and per
    post type in user meta `metaboxhidden_<post_type>` (array of box IDs).
    """

    BOXES = {
        "rank_math_metabox": "Rank Math SEO",
        "rank_math_metabox_content_ai": "Rank Math Content AI",
    }
    # What WordPress hides when the user never touched Screen Options
    # (get_hidden_meta_boxes() defaults) — kept so they don't suddenly appear.
    WP_DEFAULT_HIDDEN = [
        "slugdiv",
        "trackbacksdiv",
        "postcustom",
        "postexcerpt",
        "commentstatusdiv",
        "commentsdiv",
        "authordiv",
        "revisionsdiv",
    ]
    EXCLUDED_PREFIXES = ("wp_", "acf-")
    EXCLUDED_TYPES = ("attachment",)

    @classmethod
    def toggle(cls, post_type: str | None = None):
        user_id = cls.select_user()
        if user_id is None:
            Print.error("No user selected.")
            return
        post_type = post_type or cls.select_post_type()
        if post_type is None:
            Print.error("No post type selected.")
            return

        meta_key = f"metaboxhidden_{post_type}"
        hidden = cls.get_hidden(user_id, meta_key)

        # Both boxes are toggled together: if any is visible — hide both,
        # if both are hidden — show both.
        hide = any(box_id not in hidden for box_id in cls.BOXES)
        hidden = [box_id for box_id in hidden if box_id not in cls.BOXES]
        if hide:
            hidden.extend(cls.BOXES)
        state = "hidden" if hide else "visible"
        for label in cls.BOXES.values():
            Print.success(f"{label}: {state}")

        Command.run_quiet(
            f"wp user meta update {user_id} {meta_key} "
            f"{shlex.quote(json.dumps(hidden))} --format=json"
        )
        Print.success(
            f"Saved {meta_key} for user {user_id}. Reload the editor page.")

    @classmethod
    def get_hidden(cls, user_id: int, meta_key: str) -> list[str]:
        try:
            hidden = Command.run_json(
                f"wp user meta get {user_id} {meta_key} --format=json"
            )
        except (RuntimeError, ValueError):
            # Meta not set yet — WordPress uses its defaults.
            return list(cls.WP_DEFAULT_HIDDEN)
        if isinstance(hidden, dict):
            return list(hidden.values())
        return list(hidden or [])

    @staticmethod
    def select_user() -> int | None:
        users = Command.run_json(
            "wp user list --role=administrator --fields=ID,user_login "
            "--format=json"
        )
        if len(users) == 1:
            return int(users[0]["ID"])
        selected = Select.select_fzf_one(
            [f"{u['ID']}-{u['user_login']}" for u in users]
        )
        return int(selected.split("-")[0]) if selected else None

    @classmethod
    def select_post_type(cls) -> str | None:
        post_types = Command.run_json(
            "wp post-type list --show_ui=1 --field=name --format=json"
        )
        names = [
            name for name in post_types
            if name not in cls.EXCLUDED_TYPES
            and not name.startswith(cls.EXCLUDED_PREFIXES)
        ]
        # Pages first — this lives in the Pages menu.
        names.sort(key=lambda name: name != "page")
        return Select.select_fzf_one(names)
