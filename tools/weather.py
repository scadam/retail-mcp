def register_weather(mcp, load_json, render_widget):
    @mcp.resource("ui://widget/weather.html", mime_type="text/html+skybridge",
                  annotations={"readOnlyHint": True})
    def weather_widget() -> str:
        return render_widget("weather.html", store_name="Costa Coffee",
                             store_city="", current={}, forecast=[],
                             hourly_today=[])

    @mcp.tool()
    def get_weather_forecast(store_id: str = "GLD001", days: int = 3) -> dict:
        """Get the current weather conditions and multi-day forecast for the area
        surrounding a Costa Coffee store. Includes footfall impact predictions and
        drink demand adjustments based on weather patterns — e.g. heavy rain drives
        hot drink demand up 25% and reduces high-street footfall by up to 20%.
        Use this to proactively advise on staffing, stock prep, and product placement.

        Args:
            store_id: The store identifier (e.g., 'GLD001' for Guildford High Street)
            days: Number of forecast days to return (1-5, default 3)
        """
        weather_data = load_json("weather.json")
        stores = load_json("stores.json")
        store_info = next(
            (s for s in stores if s["store_id"] == store_id),
            {"name": store_id, "city": ""},
        )
        store_weather = weather_data.get(store_id, weather_data.get("default", {}))
        current = store_weather.get("current", {})
        forecast = store_weather.get("forecast", [])[:max(1, min(days, 5))]
        hourly = store_weather.get("hourly_today", [])

        html = render_widget(
            "weather.html",
            store_name=store_info.get("name", store_id),
            store_city=store_info.get("city", ""),
            current=current,
            forecast=forecast,
            hourly_today=hourly,
        )
        return {
            "data": {
                "store_id": store_id,
                "store_name": store_info.get("name", store_id),
                "current": current,
                "forecast": forecast,
                "footfall_impact": current.get("footfall_impact", "normal"),
                "footfall_impact_pct": current.get("footfall_impact_pct", 0),
                "drink_demand": current.get("drink_demand", {}),
                "agent_tip": current.get("agent_tip", ""),
            },
            "_meta": {
                "ui": {
                    "widget": "ui://widget/weather.html",
                    "html": html,
                    "params": {"store_id": store_id, "days": days},
                }
            },
        }
