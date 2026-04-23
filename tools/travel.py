def register_travel(mcp, load_json, render_widget):
    @mcp.resource("ui://widget/travel_updates.html", mime_type="text/html+skybridge",
                  annotations={"readOnlyHint": True})
    def travel_widget() -> str:
        return render_widget("travel_updates.html", store_name="Costa Coffee",
                             disruptions=[], local_events=[], footfall_forecast={})

    @mcp.tool()
    def get_travel_updates(store_id: str = "GLD001") -> dict:
        """Get real-time travel and transport disruption updates for the area around
        a Costa Coffee store, plus upcoming local events that drive footfall.
        Includes train delays, bus diversions, road closures, sporting events,
        festivals, and competitor openings — each with a footfall impact prediction.
        Use this to advise on staffing adjustments, stock preparation, and
        timing of promotions throughout the day.

        Args:
            store_id: The store identifier (e.g., 'GLD001' for Guildford High Street)
        """
        travel_data = load_json("travel_updates.json")
        stores = load_json("stores.json")
        store_info = next(
            (s for s in stores if s["store_id"] == store_id),
            {"name": store_id},
        )
        store_travel = travel_data.get(store_id, travel_data.get("default", {}))
        disruptions = store_travel.get("disruptions", [])
        local_events = store_travel.get("local_events", [])
        footfall_forecast = store_travel.get("footfall_forecast", {})

        html = render_widget(
            "travel_updates.html",
            store_name=store_info.get("name", store_id),
            disruptions=disruptions,
            local_events=local_events,
            footfall_forecast=footfall_forecast,
        )
        active_disruptions = [d for d in disruptions if d.get("status") == "active"]
        return {
            "data": {
                "store_id": store_id,
                "store_name": store_info.get("name", store_id),
                "disruptions": disruptions,
                "local_events": local_events,
                "footfall_forecast": footfall_forecast,
                "active_disruption_count": len(active_disruptions),
                "high_severity_count": sum(
                    1 for d in active_disruptions if d.get("severity") == "high"
                ),
            },
            "_meta": {
                "ui": {
                    "widget": "ui://widget/travel_updates.html",
                    "html": html,
                    "params": {"store_id": store_id},
                }
            },
        }
