def register_stock(mcp, load_json, render_widget):
    @mcp.resource("ui://widget/stock.html", mime_type="text/html+skybridge",
                  annotations={"readOnlyHint": True})
    def stock_widget() -> str:
        return render_widget("stock.html", store_name="Costa Coffee", stock_items=[])

    @mcp.tool()
    def get_stock_levels(store_id: str = "GLD001", category: str = "all") -> dict:
        """Get current stock levels for a store, optionally filtered by category."""
        all_stock  = load_json("stock.json")
        stores     = load_json("stores.json")
        store_info = next((s for s in stores if s["store_id"] == store_id), {"name": store_id})
        items = all_stock.get(store_id, [])
        if category != "all":
            items = [i for i in items if i.get("category","").lower() == category.lower()]
        html = render_widget("stock.html",
                             store_name=store_info.get("name", store_id),
                             stock_items=items)
        return {
            "data": {
                "store_id": store_id,
                "category_filter": category,
                "items": items,
                "critical_count": sum(1 for i in items if i["status"] == "Critical"),
                "low_count":      sum(1 for i in items if i["status"] == "Low"),
            },
            "_meta": {
                "ui": {
                    "widget": "ui://widget/stock.html",
                    "html": html,
                    "params": {"store_id": store_id, "category": category},
                }
            },
        }
