def register_weather(mcp, load_json, render_widget):
    @mcp.resource("ui://widget/weather.html", mime_type="text/html+skybridge",
                  annotations={"readOnlyHint": True})
    def weather_widget() -> str:
        return render_widget("weather.html", weather={}, store_name="Costa Coffee")

    @mcp.tool()
    def get_weather_forecast(store_id: str = "GLD001") -> dict:
        """Get the local weather forecast and footfall impact prediction for a Costa Coffee store.

        Shows current conditions, hourly forecast for today, a 3-day outlook, and any
        nearby local events (concerts, sports, markets) that will affect customer footfall.
        Use this to help baristas and managers plan staffing, stock, and promotions around
        expected busy or quiet periods.

        Args:
            store_id: The store identifier (e.g., 'GLD001' for Guildford High Street)
        """
        all_weather = load_json("weather.json")
        stores = load_json("stores.json")
        store_info = next((s for s in stores if s["store_id"] == store_id), {"name": store_id})
        weather = all_weather.get(store_id, {})
        html = render_widget("weather.html",
                             store_name=store_info.get("name", store_id),
                             weather=weather)
        return {
            "data": {
                "store_id": store_id,
                "store_name": store_info.get("name", store_id),
                "weather": weather,
            },
            "_meta": {
                "ui": {
                    "widget": "ui://widget/weather.html",
                    "html": html,
                    "params": {"store_id": store_id},
                }
            },
        }
