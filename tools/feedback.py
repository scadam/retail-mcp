from datetime import date, timedelta

def register_feedback(mcp, load_json, render_widget):
    @mcp.resource("widget://customer-feedback", mime_type="text/html+skybridge",
                  annotations={"readOnlyHint": True})
    def feedback_widget() -> str:
        return render_widget("feedback.html", store_name="Costa Coffee",
                             feedback_list=[], nps_score=0, promoters=0, passives=0,
                             detractors=0, nps_weekly_labels=[], nps_weekly_data=[],
                             star_counts=[0,0,0,0,0])

    @mcp.tool()
    def get_customer_feedback(store_id: str = "GLD001", days: int = 30) -> dict:
        """Get customer feedback and NPS data for a store."""
        all_feedback = load_json("customer_feedback.json")
        stores = load_json("stores.json")
        store_info = next((s for s in stores if s["store_id"] == store_id), {"name": store_id})
        cutoff = date.today() - timedelta(days=days)
        feedback_list = [
            f for f in all_feedback.get(store_id, [])
            if date.fromisoformat(f["date"]) >= cutoff
        ]
        # NPS calculation
        promoters  = sum(1 for f in feedback_list if f["nps_score"] >= 9)
        passives   = sum(1 for f in feedback_list if 7 <= f["nps_score"] <= 8)
        detractors = sum(1 for f in feedback_list if f["nps_score"] <= 6)
        total = max(1, len(feedback_list))
        nps_score = round(((promoters - detractors) / total) * 100)

        # Weekly NPS trend (12 weeks)
        nps_weekly_labels, nps_weekly_data = [], []
        for w in range(12):
            wk_start = date.today() - timedelta(weeks=12-w)
            wk_end   = wk_start + timedelta(days=7)
            wk_fb = [f for f in all_feedback.get(store_id, [])
                     if wk_start <= date.fromisoformat(f["date"]) < wk_end]
            if wk_fb:
                p  = sum(1 for f in wk_fb if f["nps_score"] >= 9)
                d  = sum(1 for f in wk_fb if f["nps_score"] <= 6)
                wk_nps = round(((p - d) / len(wk_fb)) * 100)
            else:
                wk_nps = 0
            nps_weekly_labels.append(wk_start.strftime("%d %b"))
            nps_weekly_data.append(wk_nps)

        star_counts = [
            sum(1 for f in feedback_list if f["star_rating"] == s) for s in range(1, 6)
        ]
        html = render_widget("feedback.html",
                             store_name=store_info.get("name", store_id),
                             feedback_list=feedback_list,
                             nps_score=nps_score,
                             promoters=promoters,
                             passives=passives,
                             detractors=detractors,
                             nps_weekly_labels=nps_weekly_labels,
                             nps_weekly_data=nps_weekly_data,
                             star_counts=star_counts)
        return {
            "data": {
                "store_id": store_id,
                "nps_score": nps_score,
                "total_reviews": len(feedback_list),
                "promoters": promoters,
                "passives": passives,
                "detractors": detractors,
                "star_counts": star_counts,
            },
            "_meta": {
                "ui": {
                    "widget": "widget://customer-feedback",
                    "html": html,
                    "params": {"store_id": store_id, "days": days},
                }
            },
        }
