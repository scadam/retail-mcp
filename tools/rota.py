from datetime import date

DAYS = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]

def register_rota(mcp, load_json, render_widget):
    @mcp.resource("ui://widget/rota.html", mime_type="text/html+skybridge",
                  annotations={"readOnlyHint": True})
    def rota_widget() -> str:
        return render_widget("rota.html", store_name="Costa Coffee",
                             rota_data={}, days=DAYS, today_name="", employee_map={})

    @mcp.tool()
    def get_shift_rota(store_id: str = "GLD001", date_str: str = "today") -> dict:
        """Get the weekly shift rota for a store."""
        all_rotas = load_json("rotas.json")
        stores    = load_json("stores.json")
        employees = load_json("employees.json")
        store_info = next((s for s in stores if s["store_id"] == store_id), {"name": store_id})
        store_rotas = all_rotas.get(store_id, [])
        # Return current week (week 2 of 4 = index 1 to represent "this week")
        rota_data = store_rotas[1] if len(store_rotas) > 1 else (store_rotas[0] if store_rotas else {})
        employee_map = {e["employee_id"]: e for e in employees if e["store_id"] == store_id}
        today_name = date.today().strftime("%A")
        html = render_widget("rota.html",
                             store_name=store_info.get("name", store_id),
                             rota_data=rota_data,
                             days=DAYS,
                             today_name=today_name,
                             employee_map=employee_map)
        return {
            "data": {
                "store_id": store_id,
                "rota": rota_data,
                "employees": list(employee_map.values()),
            },
            "_meta": {
                "ui": {
                    "widget": "ui://widget/rota.html",
                    "html": html,
                    "params": {"store_id": store_id, "date": date_str},
                }
            },
        }
