from fastmcp import FastMCP
import json
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

mcp = FastMCP(
    name="Costa Coffee Frontline Agent",
    instructions="""You are the Costa Coffee AI Assistant for frontline employees.
    You help baristas, shift managers, store managers, and regional/area managers
    with daily operations including schedules, stock, compliance, training,
    customer feedback, and performance dashboards.
    Always be friendly, practical, and action-oriented.
    When showing data, prefer using the UI widgets for rich visual display.
    Address users by their role context. Use Costa Coffee terminology
    (e.g., 'Barista Maestro' for senior baristas, 'store' not 'branch').

    You also have access to:
    - SharePoint documents (Costa policy docs, seasonal playbooks, VM standards, training materials,
      area manager visit agendas, allergen updates, HR guides) — reference these when relevant.
    - Web search — use this to find local events, competitor activity, FSA guidance updates,
      or anything else that could affect store operations or footfall.
    - Image understanding — users can upload photos (e.g., of stock rooms, displays, equipment
      faults, incidents) and you can analyse them to take action, log incidents, or spot
      compliance issues.

    KEY WORKFLOWS (widget chaining):
    - Morning brief: get_weather_forecast + get_travel_updates + get_shift_rota + get_shift_handover
    - Social monitoring: get_social_media_mentions → respond to reviews or brief the team
    - Footfall planning: get_weather_forecast + get_travel_updates → adjust rota or stock
    - Training: get_training_progress → play_training_video → update_training_progress
    - Stock: get_stock_levels → update_stock_level → log_corrective_action
    - Rota: get_shift_rota → update_rota_shift
    - Recipes: get_recipe (click allergens for allergen advice, click tip for more tips)
    - Demo reset: reset_demo(confirm=True) to restore all original data""",
)

DATA_DIR   = Path(__file__).parent / "data"
WIDGET_DIR = Path(__file__).parent / "widgets"
STATIC_DIR = Path(__file__).parent / "static"

jinja_env = Environment(loader=FileSystemLoader(str(WIDGET_DIR)))


def load_json(filename: str, filter_key: str = None, filter_value: str = None):
    with open(DATA_DIR / filename) as f:
        data = json.load(f)
    if filter_key and filter_value:
        if isinstance(data, list):
            return [item for item in data if item.get(filter_key) == filter_value]
        elif isinstance(data, dict) and filter_value in data:
            return data[filter_value]
    return data


def render_widget(template_name: str, **context) -> str:
    from branding.costa_theme import THEME
    template = jinja_env.get_template(template_name)
    return template.render(theme=THEME, **context)


from tools.dashboard import register_dashboard
from tools.rota import register_rota
from tools.stock import register_stock
from tools.recipes import register_recipes
from tools.training import register_training
from tools.compliance import register_compliance
from tools.incidents import register_incidents
from tools.feedback import register_feedback
from tools.regional import register_regional
from tools.maintenance import register_maintenance
from tools.promotions import register_promotions
from tools.shift_handover import register_shift_handover
from tools.updates import register_updates
from tools.weather import register_weather
from tools.travel import register_travel
from tools.social import register_social
from tools.reset import register_reset

register_dashboard(mcp, load_json, render_widget)
register_rota(mcp, load_json, render_widget)
register_stock(mcp, load_json, render_widget)
register_recipes(mcp, load_json, render_widget)
register_training(mcp, load_json, render_widget)
register_compliance(mcp, load_json, render_widget)
register_incidents(mcp, load_json, render_widget)
register_feedback(mcp, load_json, render_widget)
register_regional(mcp, load_json, render_widget)
register_maintenance(mcp, load_json, render_widget)
register_promotions(mcp, load_json, render_widget)
register_shift_handover(mcp, load_json, render_widget)
register_updates(mcp, load_json, render_widget)
register_weather(mcp, load_json, render_widget)
register_travel(mcp, load_json, render_widget)
register_social(mcp, load_json, render_widget)
register_reset(mcp, load_json, render_widget)


if __name__ == "__main__":
    import os
    mcp.run(
        transport="streamable-http",
        host=os.getenv("MCP_HOST", "0.0.0.0"),
        port=int(os.getenv("MCP_PORT", "8000")),
    )
