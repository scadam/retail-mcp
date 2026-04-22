from datetime import date

def register_promotions(mcp, load_json, render_widget):
    @mcp.resource("ui://widget/promotions.html", mime_type="text/html+skybridge",
                  annotations={"readOnlyHint": True})
    def promotions_widget() -> str:
        return render_widget("promotions.html", promotions=[])

    @mcp.tool()
    def get_current_promotions(store_id: str = None) -> dict:
        """Get current and upcoming promotions."""
        promotions = load_json("promotions.json")
        today = date.today()
        for p in promotions:
            start = date.fromisoformat(p.get("start_date", "2000-01-01"))
            end   = date.fromisoformat(p.get("end_date", "2099-12-31"))
            p["active"] = start <= today <= end
        html = render_widget("promotions.html", promotions=promotions)
        active = [p for p in promotions if p["active"]]
        return {
            "data": {
                "promotions": promotions,
                "active_count": len(active),
                "store_filter": store_id,
            },
            "_meta": {
                "ui": {
                    "widget": "ui://widget/promotions.html",
                    "html": html,
                    "params": {"store_id": store_id},
                }
            },
        }
