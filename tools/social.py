def register_social(mcp, load_json, render_widget):
    @mcp.resource("ui://widget/social_pulse.html", mime_type="text/html+skybridge",
                  annotations={"readOnlyHint": True})
    def social_widget() -> str:
        return render_widget("social_pulse.html", pulse={}, store_name="Costa Coffee")

    @mcp.tool()
    def get_social_pulse(store_id: str = "GLD001", days: int = 7) -> dict:
        """Get the social media pulse for a Costa Coffee store – mentions, sentiment, and trending posts.

        Aggregates mentions and sentiment from Instagram, TikTok, X (Twitter), Google Reviews,
        and TripAdvisor. Surfaces viral posts, influencer opportunities, and any complaints that
        need an urgent response. Helps managers understand the store's public reputation in real
        time and act on feedback before it escalates.

        Args:
            store_id: The store identifier (e.g., 'GLD001' for Guildford High Street)
            days: Number of days to look back (default 7)
        """
        all_pulse = load_json("social_pulse.json")
        stores = load_json("stores.json")
        store_info = next((s for s in stores if s["store_id"] == store_id), {"name": store_id})
        pulse = all_pulse.get(store_id, {})
        html = render_widget("social_pulse.html",
                             store_name=store_info.get("name", store_id),
                             pulse=pulse,
                             days=days)
        return {
            "data": {
                "store_id": store_id,
                "store_name": store_info.get("name", store_id),
                "pulse": pulse,
                "days": days,
            },
            "_meta": {
                "ui": {
                    "widget": "ui://widget/social_pulse.html",
                    "html": html,
                    "params": {"store_id": store_id, "days": days},
                }
            },
        }
