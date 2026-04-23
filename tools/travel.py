def register_travel(mcp, load_json, render_widget):
    @mcp.resource("ui://widget/travel_updates.html", mime_type="text/html+skybridge",
                  annotations={"readOnlyHint": True})
    def travel_widget() -> str:
        return render_widget("travel_updates.html", travel={}, store_name="Costa Coffee")

    @mcp.tool()
    def get_travel_updates(store_id: str = "GLD001") -> dict:
        """Get live travel and transport disruption updates affecting a Costa Coffee store.

        Returns details of rail strikes, signal failures, road closures, and major local
        events causing traffic or footfall changes near the store. Includes the impact on
        staff commutes (which team members may be delayed), expected customer footfall
        changes, and recommended actions for the shift manager.

        Args:
            store_id: The store identifier (e.g., 'GLD001' for Guildford High Street)
        """
        all_travel = load_json("travel_updates.json")
        stores = load_json("stores.json")
        store_info = next((s for s in stores if s["store_id"] == store_id), {"name": store_id})
        travel = all_travel.get(store_id, {})
        html = render_widget("travel_updates.html",
                             store_name=store_info.get("name", store_id),
                             travel=travel)
        return {
            "data": {
                "store_id": store_id,
                "store_name": store_info.get("name", store_id),
                "travel": travel,
            },
            "_meta": {
                "ui": {
                    "widget": "ui://widget/travel_updates.html",
                    "html": html,
                    "params": {"store_id": store_id},
                }
            },
        }
