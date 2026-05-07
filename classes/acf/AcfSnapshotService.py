import json
import re
from pathlib import Path


class AcfSnapshotService:
    @staticmethod
    def _slugify(title: str) -> str:
        slug = title.lower().strip()
        slug = re.sub(r"[\s_]+", "-", slug)
        slug = re.sub(r"[^a-z0-9\-]", "", slug)
        return slug

    @staticmethod
    def _extract_fields(fields: list) -> list:
        result = []
        for field in fields:
            entry: dict = {
                "name": field.get("name", ""),
                "type": field.get("type", ""),
            }
            sub = field.get("sub_fields") or field.get("fields") or []
            if sub:
                entry["sub_fields"] = AcfSnapshotService._extract_fields(sub)
            result.append(entry)
        return result

    @staticmethod
    def save(script_dir: Path, project_name: str) -> None:
        snapshot_dir = script_dir / "projects" / project_name
        snapshot_dir.mkdir(parents=True, exist_ok=True)

        for path in Path("acf").glob("*.json"):
            data = json.loads(path.read_text(encoding="utf-8"))
            for group in data:
                title = group.get("title", path.stem)
                slug = AcfSnapshotService._slugify(title)
                fields = AcfSnapshotService._extract_fields(group.get("fields", []))
                snapshot_path = snapshot_dir / f"{slug}.json"
                snapshot_path.write_text(
                    json.dumps(fields, indent=4, ensure_ascii=False),
                    encoding="utf-8",
                )
