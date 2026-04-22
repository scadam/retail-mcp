from datetime import date, timedelta
import uuid

def register_incidents(mcp, load_json, render_widget):
    @mcp.resource("widget://incident-log", mime_type="text/html+skybridge",
                  annotations={"readOnlyHint": True})
    def incident_widget() -> str:
        return render_widget("incident_log.html", store_name="Costa Coffee", incidents=[])

    @mcp.tool()
    def get_incidents(store_id: str = "GLD001", days: int = 7) -> dict:
        """Get incident log for a store over the last N days."""
        all_incidents = load_json("incidents.json")
        stores = load_json("stores.json")
        store_info = next((s for s in stores if s["store_id"] == store_id), {"name": store_id})
        cutoff = date.today() - timedelta(days=days)
        incidents = [
            i for i in all_incidents
            if i["store_id"] == store_id and date.fromisoformat(i["date"]) >= cutoff
        ]
        incidents.sort(key=lambda x: x["date"], reverse=True)
        html = render_widget("incident_log.html",
                             store_name=store_info.get("name", store_id),
                             incidents=incidents)
        return {
            "data": {
                "store_id": store_id,
                "days": days,
                "incidents": incidents,
                "total": len(incidents),
            },
            "_meta": {
                "ui": {
                    "widget": "widget://incident-log",
                    "html": html,
                    "params": {"store_id": store_id, "days": days},
                }
            },
        }

    @mcp.tool()
    def submit_incident(store_id: str, category: str, severity: str,
                        description: str, reported_by: str) -> dict:
        """Submit a new incident report for a store."""
        today = date.today()
        incident = {
            "incident_id": f"INC{str(uuid.uuid4())[:8].upper()}",
            "store_id": store_id,
            "date": today.isoformat(),
            "time": "00:00",
            "category": category,
            "severity": severity,
            "description": description,
            "reported_by": reported_by,
            "status": "Open",
            "action_taken": "Newly submitted – under review.",
            "resolution_date": None,
        }
        return {
            "data": incident,
            "message": f"Incident {incident['incident_id']} submitted successfully.",
            "_meta": {"ui": {"widget": "widget://incident-log",
                             "params": {"store_id": store_id}}},
        }
