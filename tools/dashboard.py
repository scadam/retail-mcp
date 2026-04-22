def register_dashboard(mcp, load_json, render_widget):
    @mcp.resource("widget://daily-dashboard", mime_type="text/html+skybridge",
                  annotations={"readOnlyHint": True})
    def dashboard_widget() -> str:
        return render_widget("dashboard.html", store_name="Costa Coffee", sales_data={})

    @mcp.tool()
    def get_daily_dashboard(store_id: str = "GLD001") -> dict:
        """Get the daily sales dashboard for a store."""
        all_sales = load_json("daily_sales.json")
        stores = load_json("stores.json")
        store_info = next((s for s in stores if s["store_id"] == store_id), {"name": store_id})
        store_sales = all_sales.get(store_id, [])
        today_data = store_sales[-1] if store_sales else {}
        html = render_widget("dashboard.html",
                             store_name=store_info.get("name", store_id),
                             sales_data=today_data)
        return {
            "data": {
                "store_id": store_id,
                "store_name": store_info.get("name", store_id),
                "sales": today_data,
            },
            "_meta": {
                "ui": {
                    "widget": "widget://daily-dashboard",
                    "html": html,
                    "params": {"store_id": store_id},
                }
            },
        }
