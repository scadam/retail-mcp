from datetime import date, timedelta
from pathlib import Path

def register_training(mcp, load_json, render_widget):
    @mcp.resource("ui://widget/training.html", mime_type="text/html+skybridge",
                  annotations={"readOnlyHint": True})
    def training_widget() -> str:
        return render_widget("training.html", store_name="Costa Coffee",
                             employee_view=None, team_rows=[], team_avg_pct=0,
                             overdue_count=0, due_this_week=0, progress_list=[],
                             overall_pct=0, modules_view=False, modules=[])

    @mcp.resource("ui://widget/training_video.html", mime_type="text/html+skybridge",
                  annotations={"readOnlyHint": True})
    def training_video_widget() -> str:
        return render_widget("training_video.html", module={}, progress=None, video_available=False)

    @mcp.tool()
    def get_training_modules(level: str = None) -> dict:
        """Get the full catalogue of Costa Coffee training modules, optionally filtered by level.
        Displays a visual cards view with module thumbnails, video indicators and difficulty level.
        Level options: All, Barista, Senior Barista, Shift Manager"""
        modules = load_json("training_modules.json")
        if level:
            modules = [m for m in modules if m.get("level", "").lower() == level.lower()
                       or m.get("level", "").lower() == "all"]
        html = render_widget("training.html",
                             store_name="Costa Coffee",
                             employee_view=None,
                             modules_view=True,
                             modules=modules,
                             progress_list=[],
                             overall_pct=0,
                             team_rows=[], team_avg_pct=0,
                             overdue_count=0, due_this_week=0)
        return {
            "data": {"modules": modules, "count": len(modules)},
            "_meta": {"ui": {"widget": "ui://widget/training.html", "html": html,
                             "params": {"level": level}}},
        }

    @mcp.tool()
    def play_training_video(module_id: str, employee_id: str = None) -> dict:
        """Open the video player widget for a training module.
        Shows the module thumbnail, video player (if .mp4 is deployed), module info,
        employee progress (if employee_id provided), and guided learning actions.
        This chains into a guided learning session when the user clicks 'Start guided learning'."""
        modules = load_json("training_modules.json")
        module = next((m for m in modules if m["module_id"] == module_id), None)
        if not module:
            # Try partial match by name
            module = next((m for m in modules if module_id.lower() in m["name"].lower()), None)
        if not module:
            return {
                "success": False,
                "error": f"Training module '{module_id}' not found",
                "available_modules": [m["module_id"] + ": " + m["name"] for m in modules],
            }

        # Check if the actual mp4 file exists
        media_dir = Path(__file__).parent.parent / "static" / "media"
        video_path = module.get("video", "").lstrip("/")
        video_file = Path(__file__).parent.parent / video_path if video_path else None
        video_available = bool(video_file and video_file.exists() and video_file.stat().st_size > 1000)

        # Get employee progress if requested
        progress_record = None
        if employee_id:
            all_progress = load_json("training_progress.json")
            progress_record = next(
                (p for p in all_progress if p["employee_id"] == employee_id and p["module_id"] == module_id),
                None,
            )

        html = render_widget("training_video.html",
                             module=module,
                             progress=progress_record,
                             video_available=video_available)
        return {
            "data": {
                "module": module,
                "video_available": video_available,
                "employee_id": employee_id,
                "progress": progress_record,
            },
            "_meta": {"ui": {"widget": "ui://widget/training_video.html", "html": html,
                             "params": {"module_id": module_id, "employee_id": employee_id}}},
        }

    @mcp.tool()
    def get_training_progress(employee_id: str = None, store_id: str = "GLD001") -> dict:
        """Get training progress for an employee or the whole store team."""
        modules   = load_json("training_modules.json")
        progress  = load_json("training_progress.json")
        employees = load_json("employees.json")
        stores    = load_json("stores.json")
        store_info = next((s for s in stores if s["store_id"] == store_id), {"name": store_id})
        modules_map = {m["module_id"]: m for m in modules}
        today = date.today()
        week_end = today + timedelta(days=7)

        if employee_id:
            emp = next((e for e in employees if e["employee_id"] == employee_id), None)
            emp_progress = [p for p in progress if p["employee_id"] == employee_id]
            for p in emp_progress:
                mod = modules_map.get(p["module_id"], {})
                p["module_name"] = mod.get("name", p["module_id"])
                p["module_image"] = mod.get("image", "")
            overall = int(sum(p["completion_pct"] for p in emp_progress) / max(1, len(emp_progress)))
            html = render_widget("training.html",
                                 store_name=store_info.get("name", store_id),
                                 employee_view=emp,
                                 progress_list=emp_progress,
                                 overall_pct=overall,
                                 modules_view=False, modules=[],
                                 team_rows=[], team_avg_pct=0, overdue_count=0, due_this_week=0)
            return {
                "data": {"employee_id": employee_id, "progress": emp_progress, "overall_pct": overall},
                "_meta": {"ui": {"widget": "ui://widget/training.html", "html": html,
                                 "params": {"employee_id": employee_id}}},
            }

        # Store overview
        store_emps = [e for e in employees if e["store_id"] == store_id]
        team_rows = []
        overdue_count = 0
        due_this_week = 0
        for emp in store_emps:
            emp_p = [p for p in progress if p["employee_id"] == emp["employee_id"]]
            avg = int(sum(p["completion_pct"] for p in emp_p) / max(1, len(emp_p)))
            od = sum(1 for p in emp_p if p["status"] == "Overdue")
            overdue_count += od
            due = sum(1 for p in emp_p if p["due_date"] and
                      today <= date.fromisoformat(p["due_date"]) <= week_end and p["completion_pct"] < 100)
            due_this_week += due
            team_rows.append({
                "employee_id": emp["employee_id"],
                "name": f"{emp['first_name']} {emp['last_name']}",
                "role": emp["role"],
                "pct": avg,
                "overdue": od,
            })
        team_avg = int(sum(r["pct"] for r in team_rows) / max(1, len(team_rows)))
        html = render_widget("training.html",
                             store_name=store_info.get("name", store_id),
                             employee_view=None,
                             modules_view=False, modules=[],
                             progress_list=[],
                             overall_pct=0,
                             team_rows=team_rows,
                             team_avg_pct=team_avg,
                             overdue_count=overdue_count,
                             due_this_week=due_this_week)
        return {
            "data": {"store_id": store_id, "team_avg_pct": team_avg, "team": team_rows,
                     "overdue_count": overdue_count, "due_this_week": due_this_week},
            "_meta": {"ui": {"widget": "ui://widget/training.html", "html": html,
                             "params": {"store_id": store_id}}},
        }
