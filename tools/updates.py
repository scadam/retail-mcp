"""
Tools for updating and correcting data records.
These tools allow managers to update training progress, stock levels,
rota shifts, and log corrective actions. All changes are persisted to JSON.
"""

import json
from datetime import date, datetime
from pathlib import Path


def _save_json(data_dir: Path, filename: str, data) -> None:
    with open(data_dir / filename, "w") as f:
        json.dump(data, f, indent=2)


def register_updates(mcp, load_json, render_widget):
    data_dir = Path(__file__).parent.parent / "data"

    @mcp.tool()
    def update_training_progress(
        employee_id: str,
        module_id: str,
        completion_pct: int,
        status: str = None,
        notes: str = None,
    ) -> dict:
        """Update an employee's completion percentage for a training module.
        Status is auto-calculated if not provided: 0% = Not Started,
        1-99% = In Progress, 100% = Completed.
        Saves the change permanently to the training progress data."""
        progress = load_json("training_progress.json")

        if completion_pct < 0 or completion_pct > 100:
            return {"success": False, "error": "completion_pct must be between 0 and 100"}

        if status is None:
            if completion_pct == 0:
                status = "Not Started"
            elif completion_pct == 100:
                status = "Completed"
            else:
                status = "In Progress"

        record = next(
            (p for p in progress if p["employee_id"] == employee_id and p["module_id"] == module_id),
            None,
        )
        today_str = date.today().isoformat()
        if record:
            record["completion_pct"] = completion_pct
            record["status"] = status
            if completion_pct == 100 and not record.get("completed_date"):
                record["completed_date"] = today_str
            if notes:
                record["notes"] = notes
            record["last_updated"] = today_str
        else:
            new_record = {
                "employee_id": employee_id,
                "module_id": module_id,
                "completion_pct": completion_pct,
                "status": status,
                "started_date": today_str if completion_pct > 0 else None,
                "completed_date": today_str if completion_pct == 100 else None,
                "due_date": None,
                "last_updated": today_str,
            }
            if notes:
                new_record["notes"] = notes
            progress.append(new_record)
            record = new_record

        _save_json(data_dir, "training_progress.json", progress)
        return {
            "success": True,
            "data": {
                "employee_id": employee_id,
                "module_id": module_id,
                "completion_pct": completion_pct,
                "status": status,
                "message": f"Training progress updated: {employee_id} / {module_id} → {completion_pct}% ({status})",
            },
        }

    @mcp.tool()
    def update_stock_level(
        store_id: str,
        item_id: str,
        new_level: float,
        status: str = None,
        notes: str = None,
    ) -> dict:
        """Update the current stock level for a specific item in a store.
        Status is auto-calculated based on par_level if not provided.
        Saves the change permanently to the stock data."""
        stock = load_json("stock.json")

        store_stock = stock.get(store_id)
        if not store_stock:
            return {"success": False, "error": f"Store '{store_id}' not found"}

        item = next((i for i in store_stock if i["item_id"] == item_id), None)
        if not item:
            return {"success": False, "error": f"Item '{item_id}' not found in store '{store_id}'"}

        old_level = item["current_level"]
        item["current_level"] = new_level

        if status is None:
            par = item.get("par_level", 0)
            if new_level == 0:
                status = "Critical"
            elif new_level < par * 0.5:
                status = "Critical"
            elif new_level < par:
                status = "Low"
            else:
                status = "OK"

        item["status"] = status
        item["last_updated"] = date.today().isoformat()
        if notes:
            item["notes"] = notes

        _save_json(data_dir, "stock.json", stock)
        return {
            "success": True,
            "data": {
                "store_id": store_id,
                "item_id": item_id,
                "item_name": item["name"],
                "old_level": old_level,
                "new_level": new_level,
                "status": status,
                "unit": item.get("unit", ""),
                "message": f"Stock updated: {item['name']} {old_level}→{new_level} {item.get('unit','')} ({status})",
            },
        }

    @mcp.tool()
    def update_rota_shift(
        store_id: str,
        employee_id: str,
        day: str,
        shift_type: str,
        start_time: str = None,
        week_index: int = 1,
    ) -> dict:
        """Update a specific shift for an employee in the rota.
        shift_type must be one of: Early, Mid, Late, OFF.
        day must be a full day name e.g. Monday, Tuesday.
        week_index 0=last week, 1=current week (default), 2=next week.
        Saves the change permanently to the rota data."""
        valid_shifts = {"Early", "Mid", "Late", "OFF"}
        valid_days = {"Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"}

        if shift_type not in valid_shifts:
            return {"success": False, "error": f"shift_type must be one of {valid_shifts}"}
        if day not in valid_days:
            return {"success": False, "error": f"day must be one of {valid_days}"}

        rotas = load_json("rotas.json")
        store_rotas = rotas.get(store_id)
        if not store_rotas:
            return {"success": False, "error": f"Store '{store_id}' not found"}

        if week_index >= len(store_rotas):
            return {"success": False, "error": f"week_index {week_index} out of range (max {len(store_rotas)-1})"}

        rota_week = store_rotas[week_index]
        schedule = rota_week.get("schedule", {})

        if employee_id not in schedule:
            schedule[employee_id] = {}
        rota_week["schedule"] = schedule

        shift_starts = {"Early": "05:30", "Mid": "09:00", "Late": "13:00", "OFF": None}
        if shift_type == "OFF":
            schedule[employee_id][day] = {"shift": "OFF"}
        else:
            start = start_time or shift_starts[shift_type]
            schedule[employee_id][day] = {"shift": shift_type, "start": start}

        _save_json(data_dir, "rotas.json", rotas)
        return {
            "success": True,
            "data": {
                "store_id": store_id,
                "employee_id": employee_id,
                "day": day,
                "shift_type": shift_type,
                "message": f"Rota updated: {employee_id} on {day} → {shift_type}",
            },
        }

    @mcp.tool()
    def log_corrective_action(
        store_id: str,
        action_type: str,
        description: str,
        related_id: str = None,
        priority: str = "Medium",
        assigned_to: str = None,
    ) -> dict:
        """Log a corrective action for a store. This records management actions taken
        in response to issues (stock shortfalls, training gaps, compliance failures, etc).
        action_type examples: 'stock_order', 'training_reminder', 'compliance_fix',
        'rota_change', 'customer_complaint', 'equipment_fault'.
        Saved permanently to the corrective_actions log."""
        actions_file = data_dir / "corrective_actions.json"
        if actions_file.exists():
            with open(actions_file) as f:
                actions = json.load(f)
        else:
            actions = []

        action = {
            "action_id": f"CA{len(actions) + 1:04d}",
            "store_id": store_id,
            "action_type": action_type,
            "description": description,
            "priority": priority,
            "status": "Open",
            "logged_at": datetime.now().isoformat(),
            "logged_date": date.today().isoformat(),
        }
        if related_id:
            action["related_id"] = related_id
        if assigned_to:
            action["assigned_to"] = assigned_to

        actions.append(action)
        with open(actions_file, "w") as f:
            json.dump(actions, f, indent=2)

        return {
            "success": True,
            "data": {
                "action_id": action["action_id"],
                "store_id": store_id,
                "action_type": action_type,
                "priority": priority,
                "message": f"Corrective action {action['action_id']} logged: {description}",
            },
        }

    @mcp.tool()
    def get_corrective_actions(store_id: str = None, status: str = None) -> dict:
        """Get the list of logged corrective actions, optionally filtered by store or status."""
        actions_file = data_dir / "corrective_actions.json"
        if not actions_file.exists():
            return {"data": [], "message": "No corrective actions logged yet"}

        with open(actions_file) as f:
            actions = json.load(f)

        if store_id:
            actions = [a for a in actions if a.get("store_id") == store_id]
        if status:
            actions = [a for a in actions if a.get("status", "").lower() == status.lower()]

        return {
            "data": actions,
            "count": len(actions),
            "open_count": sum(1 for a in actions if a.get("status") == "Open"),
        }

    @mcp.tool()
    def close_corrective_action(action_id: str, resolution_notes: str = None) -> dict:
        """Mark a corrective action as resolved/closed."""
        actions_file = data_dir / "corrective_actions.json"
        if not actions_file.exists():
            return {"success": False, "error": "No corrective actions file found"}

        with open(actions_file) as f:
            actions = json.load(f)

        action = next((a for a in actions if a["action_id"] == action_id), None)
        if not action:
            return {"success": False, "error": f"Action {action_id} not found"}

        action["status"] = "Closed"
        action["closed_at"] = datetime.now().isoformat()
        if resolution_notes:
            action["resolution_notes"] = resolution_notes

        with open(actions_file, "w") as f:
            json.dump(actions, f, indent=2)

        return {
            "success": True,
            "data": {"action_id": action_id, "message": f"Action {action_id} closed"},
        }
