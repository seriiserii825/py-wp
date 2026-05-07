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
    def _field_id(field: dict) -> str:
        return field.get("name") or field.get("label", "")

    @staticmethod
    def _extract_fields(fields: list) -> list:
        result = []
        for field in fields:
            entry: dict = {
                "name": AcfSnapshotService._field_id(field),
                "type": field.get("type", ""),
            }
            sub = field.get("sub_fields") or field.get("fields") or []
            if sub:
                entry["sub_fields"] = AcfSnapshotService._extract_fields(sub)
            result.append(entry)
        return result

    @staticmethod
    def save(base_dir: Path) -> None:
        snapshot_dir = base_dir / "acf-snapshots"
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

    @staticmethod
    def _apply_order(real_fields: list, snapshot_fields: list) -> list:
        by_name = {AcfSnapshotService._field_id(f): f for f in real_fields}
        ordered = []
        for snap in snapshot_fields:
            name = snap.get("name")
            if name in by_name:
                field = by_name.pop(name)
                snap_sub = snap.get("sub_fields", [])
                if snap_sub:
                    for sub_key in ("sub_fields", "fields"):
                        if field.get(sub_key):
                            field[sub_key] = AcfSnapshotService._apply_order(
                                field[sub_key], snap_sub
                            )
                            break
                ordered.append(field)
        ordered.extend(by_name.values())
        for i, field in enumerate(ordered):
            field["menu_order"] = i
        return ordered

    @staticmethod
    def reorder_from_snapshot(section_file_json_path: Path, base_dir: Path) -> None:
        data = json.loads(section_file_json_path.read_text(encoding="utf-8"))
        group = data[0]
        title = group.get("title", section_file_json_path.stem)
        slug = AcfSnapshotService._slugify(title)

        snapshot_path = base_dir / "acf-snapshots" / f"{slug}.json"
        if not snapshot_path.exists():
            raise FileNotFoundError(f"Snapshot not found: {snapshot_path}")

        snapshot_fields = json.loads(snapshot_path.read_text(encoding="utf-8"))
        group["fields"] = AcfSnapshotService._apply_order(
            group.get("fields", []), snapshot_fields
        )
        section_file_json_path.write_text(
            json.dumps(data, indent=4, ensure_ascii=False), encoding="utf-8"
        )
