"""
Demo reset tool - restores all JSON data files to their original state.
Useful for resetting the demo after testing, presentations, or as a clean start.
"""

import json
import shutil
from pathlib import Path
from datetime import datetime


def register_reset(mcp, load_json, render_widget):
    data_dir = Path(__file__).parent.parent / "data"
    backup_dir = Path(__file__).parent.parent / "data_backup"

    @mcp.tool()
    def reset_demo(confirm: bool = False, store_id: str = None) -> dict:
        """Reset the demo data back to its original state.
        This will restore all JSON data files from the backup, removing
        any updates made during the demo session.
        Set confirm=True to actually perform the reset (prevents accidental resets).
        Optionally specify store_id to only reset corrective_actions for a store,
        or leave blank to reset all data files.
        WARNING: This cannot be undone - all demo changes will be lost."""

        if not confirm:
            # List what would be reset
            backup_files = list(backup_dir.glob("*.json"))
            data_files = list(data_dir.glob("*.json"))
            non_backup = [f.name for f in data_files if f.name not in [b.name for b in backup_files]]
            return {
                "success": False,
                "message": "Set confirm=True to proceed with the reset. This will restore all original data.",
                "files_to_restore": [f.name for f in backup_files],
                "extra_files_to_remove": non_backup,
                "warning": "All demo changes (training updates, stock corrections, corrective actions) will be permanently lost.",
            }

        if not backup_dir.exists():
            return {
                "success": False,
                "error": "Backup directory not found at data_backup/. Cannot reset.",
            }

        backup_files = list(backup_dir.glob("*.json"))
        if not backup_files:
            return {
                "success": False,
                "error": "No backup files found in data_backup/",
            }

        restored = []
        errors = []

        for backup_file in backup_files:
            try:
                target = data_dir / backup_file.name
                shutil.copy2(backup_file, target)
                restored.append(backup_file.name)
            except Exception as e:
                errors.append(f"{backup_file.name}: {str(e)}")

        # Remove any extra data files not in backup (e.g. corrective_actions.json)
        removed = []
        backup_names = {f.name for f in backup_files}
        for data_file in data_dir.glob("*.json"):
            if data_file.name not in backup_names:
                try:
                    data_file.unlink()
                    removed.append(data_file.name)
                except Exception as e:
                    errors.append(f"Remove {data_file.name}: {str(e)}")

        reset_log = {
            "reset_at": datetime.now().isoformat(),
            "restored_files": restored,
            "removed_files": removed,
            "errors": errors,
        }

        return {
            "success": len(errors) == 0,
            "data": reset_log,
            "message": (
                f"✅ Demo reset complete! Restored {len(restored)} data files."
                if not errors
                else f"⚠️ Reset completed with {len(errors)} error(s). Restored {len(restored)} files."
            ),
        }

    @mcp.tool()
    def get_demo_status() -> dict:
        """Get the current demo status - shows which data files exist, when they were
        last modified, and whether any corrective actions or demo changes are present."""
        data_files = {}
        for f in sorted(data_dir.glob("*.json")):
            stat = f.stat()
            data_files[f.name] = {
                "size_kb": round(stat.st_size / 1024, 1),
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()[:19],
            }

        # Check for corrective actions
        actions_file = data_dir / "corrective_actions.json"
        corrective_actions_count = 0
        if actions_file.exists():
            with open(actions_file) as f:
                actions = json.load(f)
            corrective_actions_count = len(actions)

        return {
            "data": {
                "data_files": data_files,
                "corrective_actions_count": corrective_actions_count,
                "backup_exists": backup_dir.exists(),
                "demo_modified": corrective_actions_count > 0,
            },
            "message": (
                f"Demo has {corrective_actions_count} corrective action(s) logged. "
                f"Use reset_demo(confirm=True) to restore original data."
                if corrective_actions_count > 0
                else "Demo data is in its original state."
            ),
        }
