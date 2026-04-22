def register_maintenance(mcp, load_json, render_widget):
    @mcp.resource("widget://maintenance-requests", mime_type="text/html+skybridge",
                  annotations={"readOnlyHint": True})
    def maintenance_widget() -> str:
        return render_widget("maintenance.html", store_name="Costa Coffee", requests=[])

    @mcp.tool()
    def get_maintenance_requests(store_id: str = "GLD001", status: str = "all") -> dict:
        """Get maintenance requests for a store."""
        all_requests = load_json("maintenance_requests.json")
        stores = load_json("stores.json")
        store_info = next((s for s in stores if s["store_id"] == store_id), {"name": store_id})
        requests = [r for r in all_requests if r["store_id"] == store_id]
        if status != "all":
            requests = [r for r in requests if r["status"].lower() == status.lower()]
        html = render_widget("maintenance.html",
                             store_name=store_info.get("name", store_id),
                             requests=requests)
        return {
            "data": {
                "store_id": store_id,
                "status_filter": status,
                "requests": requests,
                "total": len(requests),
            },
            "_meta": {
                "ui": {
                    "widget": "widget://maintenance-requests",
                    "html": html,
                    "params": {"store_id": store_id, "status": status},
                }
            },
        }
