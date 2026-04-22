from datetime import date
import uuid

def register_shift_handover(mcp, load_json, render_widget):
    @mcp.resource("ui://widget/shift_handover.html", mime_type="text/html+skybridge",
                  annotations={"readOnlyHint": True})
    def handover_widget() -> str:
        return render_widget("shift_handover.html", store_name="Costa Coffee",
                             handover=None, previous_handovers=[])

    @mcp.tool()
    def get_shift_handover(store_id: str = "GLD001", shift_date: str = "today",
                           shift_type: str = "current") -> dict:
        """Get shift handover notes for a store."""
        all_handovers = load_json("shift_handovers.json")
        stores = load_json("stores.json")
        store_info = next((s for s in stores if s["store_id"] == store_id), {"name": store_id})
        if shift_date == "today":
            shift_date = date.today().isoformat()
        store_handovers = [h for h in all_handovers if h["store_id"] == store_id]
        store_handovers.sort(key=lambda h: (h["shift_date"], h["handover_time"]), reverse=True)
        # Most recent handover for today or latest
        today_handovers = [h for h in store_handovers if h["shift_date"] == shift_date]
        handover = today_handovers[0] if today_handovers else (store_handovers[0] if store_handovers else None)
        previous = [h for h in store_handovers if h != handover][:3]
        html = render_widget("shift_handover.html",
                             store_name=store_info.get("name", store_id),
                             handover=handover,
                             previous_handovers=previous)
        return {
            "data": {
                "store_id": store_id,
                "handover": handover,
                "previous_handovers": previous,
            },
            "_meta": {
                "ui": {
                    "widget": "ui://widget/shift_handover.html",
                    "html": html,
                    "params": {"store_id": store_id, "shift_date": shift_date, "shift_type": shift_type},
                }
            },
        }

    @mcp.tool()
    def submit_shift_handover(store_id: str, outgoing_shift: str, notes: str,
                               issues: list, till_reading: float, stock_alerts: list) -> dict:
        """Submit a shift handover report."""
        handover = {
            "handover_id": f"HO{str(uuid.uuid4())[:8].upper()}",
            "store_id": store_id,
            "shift_date": date.today().isoformat(),
            "shift_type": outgoing_shift,
            "outgoing_manager": "Current Manager",
            "incoming_manager": "Incoming Manager",
            "handover_time": "now",
            "till_reading": till_reading,
            "key_issues": issues,
            "stock_alerts": stock_alerts,
            "customer_issues": 0,
            "equipment_status": "All OK",
            "staff_notes": notes,
            "overall_status": "Amber" if issues else "Green",
        }
        return {
            "data": handover,
            "message": f"Shift handover {handover['handover_id']} submitted successfully.",
            "_meta": {"ui": {"widget": "ui://widget/shift_handover.html",
                             "params": {"store_id": store_id}}},
        }
