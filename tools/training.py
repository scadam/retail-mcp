from datetime import date, timedelta

def register_training(mcp, load_json, render_widget):
    @mcp.resource("ui://widget/training.html", mime_type="text/html+skybridge",
                  annotations={"readOnlyHint": True})
    def training_widget() -> str:
        return render_widget("training.html", store_name="Costa Coffee",
                             employee_view=None, team_rows=[], team_avg_pct=0,
                             overdue_count=0, due_this_week=0, progress_list=[],
                             overall_pct=0)

    @mcp.tool()
    def get_training_progress(employee_id: str = None, store_id: str = "GLD001") -> dict:
        """Get training progress for an employee or the whole store team."""
        modules   = load_json("training_modules.json")
        progress  = load_json("training_progress.json")
        employees = load_json("employees.json")
        stores    = load_json("stores.json")
        store_info = next((s for s in stores if s["store_id"] == store_id), {"name": store_id})
        modules_map = {m["module_id"]: m["name"] for m in modules}
        today = date.today()
        week_end = today + timedelta(days=7)

        if employee_id:
            emp = next((e for e in employees if e["employee_id"] == employee_id), None)
            emp_progress = [p for p in progress if p["employee_id"] == employee_id]
            for p in emp_progress:
                p["module_name"] = modules_map.get(p["module_id"], p["module_id"])
            overall = int(sum(p["completion_pct"] for p in emp_progress) / max(1, len(emp_progress)))
            html = render_widget("training.html",
                                 store_name=store_info.get("name", store_id),
                                 employee_view=emp,
                                 progress_list=emp_progress,
                                 overall_pct=overall,
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
