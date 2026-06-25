import json
import subprocess
from pathlib import Path

from classes.acf.AcfSnapshotService import AcfSnapshotService
from classes.utils.Command import Command
from classes.utils.Print import Print
from classes.utils.WPPaths import WPPaths, PathKey


class AcfTransfer:
    @staticmethod
    def push_menu_order_to_db(section_file_json_path: Path) -> int:
        """Runs json-acf-menu-order.sh to write the field order from
        section_file_json_path's top-level `fields[].key` into
        wp_posts.menu_order, since `wp acf import` does not reorder
        fields that already exist."""
        script_dir = WPPaths.get_script_dir_path()
        script = f"{script_dir}/bash-scripts/json-acf-menu-order.sh"
        section_file_json_path = Path(section_file_json_path).resolve()

        try:
            result = subprocess.run(
                [script, str(section_file_json_path)],
                check=True,
                capture_output=True,
                text=True,
            )
            print("stdout:", result.stdout)
            if result.stderr.strip():
                print("stderr:", result.stderr)
            return result.returncode
        except subprocess.CalledProcessError as e:
            Print.error(f"Error running {script}: {e}")
            print("stdout:", e.stdout)
            print("stderr:", e.stderr)
            return e.returncode

    @staticmethod
    def _sort_fields(fields: list) -> list:
        sorted_fields = sorted(fields, key=lambda f: f.get("menu_order", 0))
        for field in sorted_fields:
            for key in ("fields", "sub_fields"):
                if field.get(key):
                    field[key] = AcfTransfer._sort_fields(field[key])
        return sorted_fields

    @staticmethod
    def _sort_acf_json_files(skip_path: Path | None = None):
        for path in Path("acf").glob("*.json"):
            if skip_path and path.resolve() == skip_path.resolve():
                continue
            data = json.loads(path.read_text(encoding="utf-8"))
            for group in data:
                if group.get("fields"):
                    group["fields"] = AcfTransfer._sort_fields(group["fields"])
            path.write_text(json.dumps(data, indent=4, ensure_ascii=False), encoding="utf-8")

    @staticmethod
    def wp_export():
        try:
            Command.run_quiet("wp db check")  # check DB connection
            Command.run("rm -rf acf")
            Command.run("wp acf export --all")
            AcfTransfer._sort_acf_json_files()
            base_dir = WPPaths.get(PathKey.BASE)
            for path in Path("acf").glob("*.json"):
                try:
                    AcfSnapshotService.reorder_from_snapshot(path, base_dir)
                except FileNotFoundError:
                    pass  # no snapshot yet for this group, keep current order
            AcfSnapshotService.save(base_dir)
        except RuntimeError as e:
            Print.error(f"Error during ACF export: {e}")
            exit(1)

    @staticmethod
    def wp_import(current_section_path: Path | str | None = None):
        """Imports all acf/*.json into WordPress.

        If `current_section_path` is given, it identifies the group the user
        was just editing locally: its order must NOT be touched by the stale
        acf-snapshots/*.json (that would silently revert the edit), and only
        its own snapshot gets refreshed from the new order. Every other group
        keeps the old behavior — reordered from its existing snapshot.
        """
        try:
            Command.run_quiet("wp db check")  # check DB connection
            current_resolved = (
                Path(current_section_path).resolve() if current_section_path else None
            )
            AcfTransfer._sort_acf_json_files(skip_path=current_resolved)
            base_dir = WPPaths.get(PathKey.BASE)
            acf_paths = list(Path("acf").glob("*.json"))
            for path in acf_paths:
                if current_resolved and path.resolve() == current_resolved:
                    continue
                try:
                    AcfSnapshotService.reorder_from_snapshot(path, base_dir)
                except FileNotFoundError:
                    pass  # no snapshot yet for this group, keep current order
            if current_resolved:
                AcfSnapshotService.save(base_dir, only_path=current_resolved)
            else:
                AcfSnapshotService.save(base_dir)
            Command.run("wp acf clean")
            Command.run("wp acf import --all")
            for path in acf_paths:
                AcfTransfer.push_menu_order_to_db(path)
        except RuntimeError as e:
            Print.error(f"Error during ACF import: {e}")
            exit(1)
