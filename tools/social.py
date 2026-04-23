def register_social(mcp, load_json, render_widget):
    @mcp.resource("ui://widget/social_media.html", mime_type="text/html+skybridge",
                  annotations={"readOnlyHint": True})
    def social_widget() -> str:
        return render_widget("social_media.html", store_name="Costa Coffee",
                             mentions=[], sentiment={}, influencer_alerts=[],
                             trending_hashtags=[])

    @mcp.tool()
    def get_social_media_mentions(store_id: str = "GLD001", days: int = 7) -> dict:
        """Get recent social media mentions, sentiment analysis, and influencer alerts
        for a Costa Coffee store. Monitors Instagram, Twitter/X, TikTok, TripAdvisor,
        Google Reviews, and the Costa App. Surfaces influencer visits that need urgent
        attention, trending hashtags, unanswered negative reviews, and overall brand
        sentiment score vs last week.
        Use this to manage the store's online reputation, respond to customer
        feedback promptly, and capitalise on positive coverage.

        Args:
            store_id: The store identifier (e.g., 'GLD001' for Guildford High Street)
            days: Number of days to look back (1-30, default 7)
        """
        social_data = load_json("social_media.json")
        stores = load_json("stores.json")
        store_info = next(
            (s for s in stores if s["store_id"] == store_id),
            {"name": store_id},
        )
        store_social = social_data.get(store_id, social_data.get("default", {}))
        mentions = store_social.get("mentions", [])
        sentiment = store_social.get("sentiment_summary", {})
        influencer_alerts = store_social.get("influencer_alerts", [])
        trending_hashtags = store_social.get("trending_hashtags", [])
        response_templates = store_social.get("response_templates", {})

        response_overdue_mentions = [
            m for m in mentions
            if m.get("requires_response") and m.get("response_overdue")
        ]

        html = render_widget(
            "social_media.html",
            store_name=store_info.get("name", store_id),
            mentions=mentions,
            sentiment=sentiment,
            influencer_alerts=influencer_alerts,
            trending_hashtags=trending_hashtags,
        )
        return {
            "data": {
                "store_id": store_id,
                "store_name": store_info.get("name", store_id),
                "mentions": mentions,
                "sentiment_summary": sentiment,
                "influencer_alerts": influencer_alerts,
                "trending_hashtags": trending_hashtags,
                "response_templates": response_templates,
                "total_mentions": len(mentions),
                "response_overdue_count": len(response_overdue_mentions),
                "response_overdue_mentions": response_overdue_mentions,
                "high_urgency_influencers": [
                    a for a in influencer_alerts if a.get("urgency") == "high"
                ],
            },
            "_meta": {
                "ui": {
                    "widget": "ui://widget/social_media.html",
                    "html": html,
                    "params": {"store_id": store_id, "days": days},
                }
            },
        }
