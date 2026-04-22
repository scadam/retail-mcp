def register_regional(mcp, load_json, render_widget):
    @mcp.resource("ui://widget/regional_benchmarks.html", mime_type="text/html+skybridge",
                  annotations={"readOnlyHint": True})
    def regional_widget() -> str:
        return render_widget("regional_benchmarks.html", region="South East",
                             stores_data=[], avg_sales=0, avg_nps=0,
                             avg_compliance=0, avg_transaction=0, avg_transactions=0)

    @mcp.tool()
    def get_regional_benchmarks(region: str = "South East") -> dict:
        """Get regional performance benchmarks comparing all stores in a region."""
        kpis = load_json("regional_kpis.json")
        stores_data = kpis.get(region, [])
        # Sort by latest weekly sales descending
        stores_data = sorted(stores_data,
                             key=lambda s: s["weekly_kpis"][-1]["weekly_sales"] if s["weekly_kpis"] else 0,
                             reverse=True)
        latest_list = [s["weekly_kpis"][-1] for s in stores_data if s["weekly_kpis"]]
        n = max(1, len(latest_list))
        avg_sales       = round(sum(l["weekly_sales"] for l in latest_list) / n, 2)
        avg_nps         = round(sum(l["nps"] for l in latest_list) / n, 1)
        avg_compliance  = round(sum(l["compliance_score_pct"] for l in latest_list) / n, 1)
        avg_transaction = round(sum(l["avg_transaction"] for l in latest_list) / n, 2)
        avg_transactions= round(sum(l["transactions"] for l in latest_list) / n)
        html = render_widget("regional_benchmarks.html",
                             region=region,
                             stores_data=stores_data,
                             avg_sales=avg_sales,
                             avg_nps=avg_nps,
                             avg_compliance=avg_compliance,
                             avg_transaction=avg_transaction,
                             avg_transactions=avg_transactions)
        return {
            "data": {
                "region": region,
                "stores": len(stores_data),
                "avg_weekly_sales": avg_sales,
                "avg_nps": avg_nps,
                "avg_compliance_pct": avg_compliance,
                "stores_data": stores_data,
            },
            "_meta": {
                "ui": {
                    "widget": "ui://widget/regional_benchmarks.html",
                    "html": html,
                    "params": {"region": region},
                }
            },
        }
