CHECKLIST_LABELS = {
    "daily_opening": "Daily Opening",
    "daily_closing": "Daily Closing",
    "weekly_deep_clean": "Weekly Deep Clean",
    "monthly_equipment": "Monthly Equipment",
    "food_safety_audit": "Food Safety Audit",
}

def register_compliance(mcp, load_json, render_widget):
    @mcp.resource("widget://compliance-checklist", mime_type="text/html+skybridge",
                  annotations={"readOnlyHint": True})
    def compliance_widget() -> str:
        return render_widget("compliance_checklist.html", store_name="Costa Coffee",
                             checklist_types=[], checklist_data={}, active_type="daily_opening")

    @mcp.tool()
    def get_compliance_checklist(store_id: str = "GLD001",
                                 checklist_type: str = "daily_opening") -> dict:
        """Get compliance checklist status for a store."""
        all_checklists = load_json("compliance_checklists.json")
        stores    = load_json("stores.json")
        store_info = next((s for s in stores if s["store_id"] == store_id), {"name": store_id})
        store_cl = all_checklists.get(store_id, {})
        checklist_types = [
            {"key": k, "label": v}
            for k, v in CHECKLIST_LABELS.items()
            if k in store_cl
        ]
        html = render_widget("compliance_checklist.html",
                             store_name=store_info.get("name", store_id),
                             checklist_types=checklist_types,
                             checklist_data=store_cl,
                             active_type=checklist_type)
        selected = store_cl.get(checklist_type, {})
        return {
            "data": {
                "store_id": store_id,
                "checklist_type": checklist_type,
                "latest": selected.get("latest", {}),
                "items": selected.get("items", []),
            },
            "_meta": {
                "ui": {
                    "widget": "widget://compliance-checklist",
                    "html": html,
                    "params": {"store_id": store_id, "checklist_type": checklist_type},
                }
            },
        }
