#!/usr/bin/env python3
"""
Costa Coffee Widget Preview Server
====================================
Run this script to preview all widgets in your local VS Code browser.

Usage:
    python widget-preview.py

Then open: http://localhost:5050

The server renders each widget using the same Jinja2 templates and sample data
as the MCP server, giving a faithful preview of how they'll appear in Copilot.

Requirements: pip install jinja2 (already in requirements.txt)
"""

import json
import sys
import os
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import mimetypes

# ── Paths ────────────────────────────────────────────────────────────────────
ROOT = Path(__file__).parent
DATA_DIR = ROOT / "data"
WIDGET_DIR = ROOT / "widgets"
STATIC_DIR = ROOT / "static"

# ── Jinja2 setup ─────────────────────────────────────────────────────────────
try:
    from jinja2 import Environment, FileSystemLoader
except ImportError:
    print("Error: jinja2 is required. Run: pip install jinja2")
    sys.exit(1)

sys.path.insert(0, str(ROOT))
from branding.costa_theme import THEME

jinja_env = Environment(loader=FileSystemLoader(str(WIDGET_DIR)))


def load_json(filename: str):
    path = DATA_DIR / filename
    if not path.exists():
        return {}
    with open(path) as f:
        return json.load(f)


def render_widget(template_name: str, **context) -> str:
    template = jinja_env.get_template(template_name)
    return template.render(theme=THEME, **context)


# ── Widget renderers ─────────────────────────────────────────────────────────

def render_dashboard(params: dict) -> str:
    sales = load_json("daily_sales.json")
    stores = load_json("stores.json")
    store_id = params.get("store_id", ["GLD001"])[0]
    store_list = sales.get(store_id, [])
    store_data = store_list[-1] if store_list else {}
    store_info = next((s for s in stores if s["store_id"] == store_id), {"name": store_id})
    return render_widget("dashboard.html",
                         store_name=store_info.get("name", store_id),
                         sales_data=store_data)


def render_rota(params: dict) -> str:
    from datetime import date
    DAYS = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    all_rotas = load_json("rotas.json")
    stores = load_json("stores.json")
    employees = load_json("employees.json")
    store_id = params.get("store_id", ["GLD001"])[0]
    store_info = next((s for s in stores if s["store_id"] == store_id), {"name": store_id})
    store_rotas = all_rotas.get(store_id, [])
    rota_data = store_rotas[1] if len(store_rotas) > 1 else (store_rotas[0] if store_rotas else {})
    employee_map = {e["employee_id"]: e for e in employees if e["store_id"] == store_id}
    today_name = date.today().strftime("%A")
    return render_widget("rota.html",
                         store_name=store_info.get("name", store_id),
                         rota_data=rota_data,
                         days=DAYS,
                         today_name=today_name,
                         employee_map=employee_map)


def render_stock(params: dict) -> str:
    stock = load_json("stock.json")
    stores = load_json("stores.json")
    store_id = params.get("store_id", ["GLD001"])[0]
    store_info = next((s for s in stores if s["store_id"] == store_id), {"name": store_id})
    store_stock = stock.get(store_id, [])
    return render_widget("stock.html",
                         store_name=store_info.get("name", store_id),
                         store_id=store_id,
                         stock_items=store_stock)


def render_recipe(params: dict) -> str:
    recipes = load_json("recipes.json")
    item_name = params.get("item_name", ["Flat White"])[0]
    recipe = next((r for r in recipes if item_name.lower() in r["name"].lower()), recipes[0] if recipes else {})
    return render_widget("recipe_card.html", recipe=recipe)


def render_training(params: dict) -> str:
    from datetime import date, timedelta
    modules = load_json("training_modules.json")
    progress = load_json("training_progress.json")
    employees = load_json("employees.json")
    stores = load_json("stores.json")
    store_id = params.get("store_id", ["GLD001"])[0]
    employee_id = params.get("employee_id", [None])[0]
    view = params.get("view", ["overview"])[0]

    store_info = next((s for s in stores if s["store_id"] == store_id), {"name": store_id})
    modules_map = {m["module_id"]: m for m in modules}

    if view == "modules":
        return render_widget("training.html",
                             store_name=store_info.get("name", store_id),
                             employee_view=None,
                             modules_view=True,
                             modules=modules,
                             progress_list=[],
                             overall_pct=0,
                             team_rows=[], team_avg_pct=0, overdue_count=0, due_this_week=0)

    if employee_id:
        emp = next((e for e in employees if e["employee_id"] == employee_id), employees[0] if employees else {})
        emp_progress = [p for p in progress if p["employee_id"] == (employee_id or (employees[0]["employee_id"] if employees else ""))]
        for p in emp_progress:
            mod = modules_map.get(p["module_id"], {})
            p["module_name"] = mod.get("name", p["module_id"])
            p["module_image"] = mod.get("image", "")
        overall = int(sum(p["completion_pct"] for p in emp_progress) / max(1, len(emp_progress)))
        return render_widget("training.html",
                             store_name=store_info.get("name", store_id),
                             employee_view=emp,
                             progress_list=emp_progress,
                             overall_pct=overall,
                             modules_view=False, modules=[],
                             team_rows=[], team_avg_pct=0, overdue_count=0, due_this_week=0)

    # Store overview
    today = date.today()
    week_end = today + timedelta(days=7)
    store_emps = [e for e in employees if e["store_id"] == store_id]
    team_rows = []
    overdue_count = 0
    due_this_week = 0
    for emp in store_emps:
        emp_p = [p for p in progress if p["employee_id"] == emp["employee_id"]]
        avg = int(sum(p["completion_pct"] for p in emp_p) / max(1, len(emp_p)))
        od = sum(1 for p in emp_p if p["status"] == "Overdue")
        overdue_count += od
        due = sum(1 for p in emp_p if p["due_date"] and
                  today <= date.fromisoformat(p["due_date"]) <= week_end and p["completion_pct"] < 100)
        due_this_week += due
        team_rows.append({
            "employee_id": emp["employee_id"],
            "name": f"{emp['first_name']} {emp['last_name']}",
            "role": emp["role"],
            "pct": avg,
            "overdue": od,
        })
    team_avg = int(sum(r["pct"] for r in team_rows) / max(1, len(team_rows))) if team_rows else 0
    return render_widget("training.html",
                         store_name=store_info.get("name", store_id),
                         employee_view=None,
                         modules_view=False, modules=[],
                         progress_list=[],
                         overall_pct=0,
                         team_rows=team_rows,
                         team_avg_pct=team_avg,
                         overdue_count=overdue_count,
                         due_this_week=due_this_week)


def render_training_video(params: dict) -> str:
    modules = load_json("training_modules.json")
    progress = load_json("training_progress.json")
    module_id = params.get("module_id", ["TM001"])[0]
    employee_id = params.get("employee_id", [None])[0]
    module = next((m for m in modules if m["module_id"] == module_id), modules[0] if modules else {})
    progress_record = None
    if employee_id:
        progress_record = next(
            (p for p in progress if p["employee_id"] == employee_id and p["module_id"] == module_id),
            None,
        )
    video_path = module.get("video", "").lstrip("/")
    video_file = ROOT / video_path if video_path else None
    video_available = bool(video_file and video_file.exists() and video_file.stat().st_size > 1000)
    return render_widget("training_video.html",
                         module=module,
                         progress=progress_record,
                         video_available=video_available)


def render_compliance(params: dict) -> str:
    _CHECKLIST_LABELS = {
        "daily_opening": "Daily Opening",
        "daily_closing": "Daily Closing",
        "weekly_deep_clean": "Weekly Deep Clean",
        "monthly_equipment": "Monthly Equipment",
        "food_safety_audit": "Food Safety Audit",
    }
    checklists = load_json("compliance_checklists.json")
    stores = load_json("stores.json")
    store_id = params.get("store_id", ["GLD001"])[0]
    store_info = next((s for s in stores if s["store_id"] == store_id), {"name": store_id})
    store_cl = checklists.get(store_id, {})
    checklist_types = [{"key": k, "label": v} for k, v in _CHECKLIST_LABELS.items() if k in store_cl]
    return render_widget("compliance_checklist.html",
                         store_name=store_info.get("name", store_id),
                         checklist_types=checklist_types,
                         checklist_data=store_cl,
                         active_type=params.get("checklist_type", ["daily_opening"])[0])


def render_incidents(params: dict) -> str:
    incidents = load_json("incidents.json")
    stores = load_json("stores.json")
    store_id = params.get("store_id", ["GLD001"])[0]
    store_info = next((s for s in stores if s["store_id"] == store_id), {"name": store_id})
    store_incidents = [i for i in incidents if i.get("store_id") == store_id]
    return render_widget("incident_log.html",
                         store_name=store_info.get("name", store_id),
                         incidents=store_incidents)


def render_feedback(params: dict) -> str:
    from datetime import date, timedelta
    all_feedback = load_json("customer_feedback.json")
    stores = load_json("stores.json")
    store_id = params.get("store_id", ["GLD001"])[0]
    store_info = next((s for s in stores if s["store_id"] == store_id), {"name": store_id})
    cutoff = date.today() - timedelta(days=30)
    feedback_list = [f for f in all_feedback.get(store_id, [])
                     if date.fromisoformat(f["date"]) >= cutoff]
    promoters  = sum(1 for f in feedback_list if f["nps_score"] >= 9)
    passives   = sum(1 for f in feedback_list if 7 <= f["nps_score"] <= 8)
    detractors = sum(1 for f in feedback_list if f["nps_score"] <= 6)
    total = max(1, len(feedback_list))
    nps_score = round(((promoters - detractors) / total) * 100)
    nps_weekly_labels, nps_weekly_data = [], []
    for w in range(12):
        wk_start = date.today() - timedelta(weeks=12-w)
        wk_end = wk_start + timedelta(days=7)
        wk_fb = [f for f in all_feedback.get(store_id, [])
                 if wk_start <= date.fromisoformat(f["date"]) < wk_end]
        p = sum(1 for f in wk_fb if f["nps_score"] >= 9)
        d = sum(1 for f in wk_fb if f["nps_score"] <= 6)
        wk_nps = round(((p - d) / len(wk_fb)) * 100) if wk_fb else 0
        nps_weekly_labels.append(wk_start.strftime("%d %b"))
        nps_weekly_data.append(wk_nps)
    star_counts = [sum(1 for f in feedback_list if f["star_rating"] == s) for s in range(1, 6)]
    return render_widget("feedback.html",
                         store_name=store_info.get("name", store_id),
                         feedback_list=feedback_list,
                         nps_score=nps_score,
                         promoters=promoters, passives=passives, detractors=detractors,
                         nps_weekly_labels=nps_weekly_labels,
                         nps_weekly_data=nps_weekly_data,
                         star_counts=star_counts)


def render_regional(params: dict) -> str:
    kpis = load_json("regional_kpis.json")
    region = params.get("region", ["South East"])[0]
    stores_data = kpis.get(region, [])
    stores_data = sorted(stores_data,
                         key=lambda s: s["weekly_kpis"][-1]["weekly_sales"] if s.get("weekly_kpis") else 0,
                         reverse=True)
    latest_list = [s["weekly_kpis"][-1] for s in stores_data if s.get("weekly_kpis")]
    n = max(1, len(latest_list))
    avg_sales = round(sum(l["weekly_sales"] for l in latest_list) / n, 2)
    avg_nps = round(sum(l["nps"] for l in latest_list) / n, 1)
    avg_compliance = round(sum(l["compliance_score_pct"] for l in latest_list) / n, 1)
    avg_transaction = round(sum(l["avg_transaction"] for l in latest_list) / n, 2)
    avg_transactions = round(sum(l["transactions"] for l in latest_list) / n)
    return render_widget("regional_benchmarks.html",
                         region=region,
                         stores_data=stores_data,
                         avg_sales=avg_sales,
                         avg_nps=avg_nps,
                         avg_compliance=avg_compliance,
                         avg_transaction=avg_transaction,
                         avg_transactions=avg_transactions)


def render_maintenance(params: dict) -> str:
    requests = load_json("maintenance_requests.json")
    stores = load_json("stores.json")
    store_id = params.get("store_id", ["GLD001"])[0]
    store_info = next((s for s in stores if s["store_id"] == store_id), {"name": store_id})
    store_reqs = [r for r in requests if r.get("store_id") == store_id]
    return render_widget("maintenance.html",
                         store_name=store_info.get("name", store_id),
                         requests=store_reqs)


def render_promotions(params: dict) -> str:
    promos = load_json("promotions.json")
    return render_widget("promotions.html", promotions=promos)


def render_shift_handover(params: dict) -> str:
    handovers = load_json("shift_handovers.json")
    stores = load_json("stores.json")
    store_id = params.get("store_id", ["GLD001"])[0]
    store_info = next((s for s in stores if s["store_id"] == store_id), {"name": store_id})
    store_handovers = [h for h in handovers if h.get("store_id") == store_id]
    latest = store_handovers[-1] if store_handovers else {}
    return render_widget("shift_handover.html",
                         store_name=store_info.get("name", store_id),
                         handover=latest)


# ── Widget registry ───────────────────────────────────────────────────────────
WIDGETS = {
    "dashboard": {
        "label": "📊 Dashboard",
        "render": render_dashboard,
        "description": "Daily sales KPIs, hourly chart, top products",
        "params": [("store_id", "GLD001")],
    },
    "rota": {
        "label": "📅 Shift Rota",
        "render": render_rota,
        "description": "Weekly shift grid with crew avatars and overtime flags",
        "params": [("store_id", "GLD001")],
    },
    "stock": {
        "label": "📦 Stock Levels",
        "render": render_stock,
        "description": "Real-time stock with category icons, critical alerts and order button",
        "params": [("store_id", "GLD001")],
    },
    "recipe": {
        "label": "👨‍🍳 Recipe Card",
        "render": render_recipe,
        "description": "Full recipe card with drink image, allergens and barista tips",
        "params": [("item_name", "Flat White")],
        "variants": [
            ("Flat White", "?widget=recipe&item_name=Flat+White"),
            ("Latte", "?widget=recipe&item_name=Latte"),
            ("Cappuccino", "?widget=recipe&item_name=Cappuccino"),
            ("Caramel Latte", "?widget=recipe&item_name=Caramel+Latte"),
            ("Mocha", "?widget=recipe&item_name=Mocha"),
            ("Hot Chocolate", "?widget=recipe&item_name=Hot+Chocolate"),
        ],
    },
    "training": {
        "label": "🎓 Training Progress",
        "render": render_training,
        "description": "Store team training overview with crew avatars",
        "params": [("store_id", "GLD001")],
        "variants": [
            ("Store Overview", "?widget=training&store_id=GLD001"),
            ("Employee Detail", "?widget=training&store_id=GLD001&employee_id=EMP001"),
            ("Module Catalogue", "?widget=training&view=modules"),
        ],
    },
    "training_video": {
        "label": "▶️ Training Video",
        "render": render_training_video,
        "description": "Training video player with progress tracking and guided actions",
        "params": [("module_id", "TM001"), ("employee_id", "EMP001")],
        "variants": [
            ("Onboarding", "?widget=training_video&module_id=TM001&employee_id=EMP001"),
            ("Coffee Mastery L1", "?widget=training_video&module_id=TM002&employee_id=EMP002"),
            ("Food Safety", "?widget=training_video&module_id=TM004"),
            ("Fire Safety", "?widget=training_video&module_id=TM011"),
        ],
    },
    "compliance": {
        "label": "✅ Compliance",
        "render": render_compliance,
        "description": "Daily/weekly/monthly compliance checklists",
        "params": [("store_id", "GLD001")],
    },
    "incidents": {
        "label": "⚠️ Incidents",
        "render": render_incidents,
        "description": "Incident log and reporting",
        "params": [("store_id", "GLD001")],
    },
    "feedback": {
        "label": "💬 Customer Feedback",
        "render": render_feedback,
        "description": "NPS, star ratings, trend analysis and recent reviews",
        "params": [("store_id", "GLD001")],
    },
    "regional": {
        "label": "🗺️ Regional Benchmarks",
        "render": render_regional,
        "description": "Cross-store performance comparison",
        "params": [],
    },
    "maintenance": {
        "label": "🔧 Maintenance",
        "render": render_maintenance,
        "description": "Kanban-style maintenance request tracker",
        "params": [("store_id", "GLD001")],
    },
    "promotions": {
        "label": "📣 Promotions",
        "render": render_promotions,
        "description": "Active offers, POS codes and promotional guidance",
        "params": [],
    },
    "shift_handover": {
        "label": "🔄 Shift Handover",
        "render": render_shift_handover,
        "description": "Shift handover notes and action items",
        "params": [("store_id", "GLD001")],
    },
}


# ── Preview navigation page ───────────────────────────────────────────────────
NAV_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Costa Coffee Widget Preview</title>
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@600;700&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<style>
  :root { --maroon:#6B1C23; --gold:#C8A951; --cream:#F5F0E8; }
  * { box-sizing:border-box; margin:0; padding:0; }
  body { font-family:'Inter',sans-serif; background:var(--cream); color:#2C1810; }
  header { background:var(--maroon); color:white; padding:16px 24px; display:flex; align-items:center; gap:16px; }
  header h1 { font-family:'Poppins',sans-serif; font-size:18px; }
  header span { font-size:12px; opacity:0.7; }
  .container { display:grid; grid-template-columns:260px 1fr; min-height:calc(100vh - 60px); }
  .sidebar { background:white; border-right:1px solid #e0d8cc; padding:16px; overflow-y:auto; }
  .sidebar h2 { font-family:'Poppins',sans-serif; font-size:11px; text-transform:uppercase; letter-spacing:.08em; color:#888; margin-bottom:10px; }
  .widget-link { display:block; padding:10px 12px; border-radius:8px; text-decoration:none; color:inherit; margin-bottom:4px; font-size:13px; font-weight:500; border:1px solid transparent; transition:all .15s; }
  .widget-link:hover { background:var(--cream); border-color:#e0d8cc; }
  .widget-link.active { background:var(--maroon); color:white; }
  .widget-link .desc { font-size:11px; opacity:.7; margin-top:2px; }
  .variants { margin-top:4px; margin-left:12px; }
  .variant-link { display:block; padding:5px 10px; font-size:11px; color:var(--maroon); text-decoration:none; border-radius:6px; }
  .variant-link:hover { background:var(--cream); }
  .preview { padding:0; background:#f0ece4; overflow-y:auto; }
  .preview-header { background:white; border-bottom:1px solid #e0d8cc; padding:12px 20px; font-size:12px; color:#666; display:flex; align-items:center; justify-content:space-between; }
  .preview-frame-wrap { padding:20px; display:flex; justify-content:center; }
  .preview-frame { background:white; border-radius:16px; box-shadow:0 4px 30px rgba(44,24,16,.15); width:420px; min-height:600px; overflow:hidden; }
  iframe { width:420px; min-height:700px; border:none; display:block; }
  .badge { background:var(--gold); color:#2C1810; padding:2px 8px; border-radius:12px; font-size:10px; font-weight:700; }
  @media(max-width:700px) { .container { grid-template-columns:1fr; } .sidebar { display:none; } }
</style>
</head>
<body>
<header>
  <div>☕</div>
  <h1>Costa Coffee Widget Preview</h1>
  <span class="badge">LOCAL DEV</span>
</header>
<div class="container">
  <nav class="sidebar">
    <h2>Widgets</h2>
    {nav}
  </nav>
  <div class="preview">
    <div class="preview-header">
      <span id="preview-label">Select a widget</span>
      <a id="open-tab" href="#" target="_blank" style="font-size:12px;color:var(--maroon);text-decoration:none">↗ Open in tab</a>
    </div>
    <div class="preview-frame-wrap">
      <div class="preview-frame">
        <iframe id="preview-iframe" src="" title="Widget preview"></iframe>
      </div>
    </div>
  </div>
</div>
<script>
function loadWidget(url, label) {
  document.getElementById('preview-iframe').src = url;
  document.getElementById('preview-label').textContent = label;
  document.getElementById('open-tab').href = url;
  document.querySelectorAll('.widget-link').forEach(el => el.classList.remove('active'));
}
// Auto-load first widget
window.addEventListener('load', function() {
  const first = document.querySelector('.widget-link');
  if (first) first.click();
});
</script>
</body>
</html>
"""


def build_nav():
    items = []
    for key, cfg in WIDGETS.items():
        params = "&".join(f"{k}={v}" for k, v in cfg.get("params", []))
        url = f"?widget={key}" + (f"&{params}" if params else "")
        label = cfg["label"]
        desc = cfg.get("description", "")
        items.append(
            f'<a class="widget-link" href="javascript:void(0)" onclick="loadWidget(\'{url}\',\'{label}\')">'
            f'{label}<div class="desc">{desc}</div></a>'
        )
        if cfg.get("variants"):
            items.append('<div class="variants">')
            for v_label, v_url in cfg["variants"]:
                items.append(
                    f'<a class="variant-link" href="javascript:void(0)" onclick="loadWidget(\'{v_url}\',\'{v_label}\')">↳ {v_label}</a>'
                )
            items.append("</div>")
    return "\n".join(items)


# ── HTTP handler ──────────────────────────────────────────────────────────────
class PreviewHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # suppress access logs

    def send_html(self, content: str, status: int = 200):
        encoded = content.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def send_file(self, path: Path):
        mime, _ = mimetypes.guess_type(str(path))
        mime = mime or "application/octet-stream"
        data = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", mime)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)

        # ── Static files ──────────────────────────────────────────────────
        if parsed.path.startswith("/static/"):
            rel_path = parsed.path.lstrip("/")
            full_path = ROOT / rel_path
            if full_path.exists() and full_path.is_file():
                self.send_file(full_path)
            else:
                self.send_html("<h1>404</h1>", 404)
            return

        # ── Navigation page ───────────────────────────────────────────────
        if not params.get("widget"):
            nav = build_nav()
            self.send_html(NAV_HTML.replace("{nav}", nav))
            return

        # ── Widget rendering ──────────────────────────────────────────────
        widget_key = params.get("widget", [""])[0]
        cfg = WIDGETS.get(widget_key)
        if not cfg:
            self.send_html(f"<h1>Unknown widget: {widget_key}</h1>", 404)
            return

        try:
            html = cfg["render"](params)
            self.send_html(html)
        except Exception as exc:
            import traceback
            tb = traceback.format_exc()
            self.send_html(
                f"<pre style='font-size:12px;padding:20px;color:red'>"
                f"Error rendering {widget_key}:\n{exc}\n\n{tb}</pre>",
                500,
            )


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5050))
    server = HTTPServer(("0.0.0.0", port), PreviewHandler)
    print(f"\n☕ Costa Coffee Widget Preview Server")
    print(f"   Open in VS Code Simple Browser: http://localhost:{port}")
    print(f"   Press Ctrl+C to stop\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
