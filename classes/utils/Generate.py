import random
import string


class Generate:
    @staticmethod
    def get_group_id() -> str:
        id = "".join(
            [random.choice(string.ascii_letters + string.digits)
             for _ in range(13)]
        )
        field_id = f"group_{id}".lower()
        return field_id
