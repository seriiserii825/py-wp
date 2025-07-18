import json


class FieldRepository:
    def __init__(self, path: str):
        self.path = path

    def load(self) -> list:
        with open(self.path, "r", encoding="utf-8") as f:
            return json.load(f)

    def save(self, data: list):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    def get_fields(self) -> list:
        return self.load()[0].get("fields", [])
