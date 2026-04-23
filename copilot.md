# Costa Coffee Frontline AI Agent â€” MCP Server

## Project Identity

- **Name**: `costa-frontline-mcp`
- **Description**: A cutting-edge MCP (Model Context Protocol) server for Costa Coffee frontline employees, built with FastMCP (Python), serving rich interactive UI widgets via the Skybridge protocol. Designed as a demo to showcase how an AI chat agent transforms daily operations for baristas, shift managers, store managers, and regional/area managers.
- **Repo**: Self-contained, single-repo, zero external dependencies beyond Python packages.
- **Auth**: NoAuth (demo server).

---

## Technical Architecture

### Stack

| Layer              | Technology                                                                 |
|--------------------|---------------------------------------------------------------------------|
| MCP Framework      | FastMCP (Python) â€” latest version, using decorators for tools & resources |
| Data Backend       | Local JSON files in `/data/` directory                                    |
| UI Widgets         | HTML + CSS + vanilla JS, served as MCP resources with mimeType `text/html+skybridge` |
| Widget Annotations | `readOnlyHint: true` on all widget resources                             |
| Full-screen Support| OpenAI Apps SDK â€” each widget includes a maximise icon (top-right corner) that expands the widget to full-screen within the host client |
| Deployment         | Azure Container Apps (single `deploy.sh` script, creates all infra)      |
| Container          | Docker (Python 3.12 slim)                                                |

### MCP Server Structure

```
costa-frontline-mcp/
â”œâ”€â”€ copilot.md                    # This file
â”œâ”€â”€ server.py                     # FastMCP server entry point
â”œâ”€â”€ tools/                        # Tool implementations (one file per domain)
â”‚   â”œâ”€â”€ __init__.py
â”‚   â”œâ”€â”€ dashboard.py
â”‚   â”œâ”€â”€ rota.py
â”‚   â”œâ”€â”€ stock.py
â”‚   â”œâ”€â”€ recipes.py
â”‚   â”œâ”€â”€ training.py
â”‚   â”œâ”€â”€ compliance.py
â”‚   â”œâ”€â”€ incidents.py
â”‚   â”œâ”€â”€ feedback.py
â”‚   â”œâ”€â”€ regional.py
â”‚   â”œâ”€â”€ maintenance.py
â”‚   â”œâ”€â”€ promotions.py
â”‚   â””â”€â”€ shift_handover.py
â”œâ”€â”€ widgets/                      # HTML widget templates (Jinja2)
â”‚   â”œâ”€â”€ base.html                 # Base template with Costa branding + Apps SDK maximise logic
â”‚   â”œâ”€â”€ dashboard.html
â”‚   â”œâ”€â”€ rota.html
â”‚   â”œâ”€â”€ stock.html
â”‚   â”œâ”€â”€ recipe_card.html
â”‚   â”œâ”€â”€ training.html
â”‚   â”œâ”€â”€ compliance_checklist.html
â”‚   â”œâ”€â”€ incident_log.html
â”‚   â”œâ”€â”€ feedback.html
â”‚   â”œâ”€â”€ regional_benchmarks.html
â”‚   â”œâ”€â”€ maintenance.html
â”‚   â”œâ”€â”€ promotions.html
â”‚   â””â”€â”€ shift_handover.html
â”œâ”€â”€ data/                         # JSON sample data files
â”‚   â”œâ”€â”€ stores.json
â”‚   â”œâ”€â”€ employees.json
â”‚   â”œâ”€â”€ rotas.json
â”‚   â”œâ”€â”€ stock.json
â”‚   â”œâ”€â”€ recipes.json
â”‚   â”œâ”€â”€ training_modules.json
â”‚   â”œâ”€â”€ training_progress.json
â”‚   â”œâ”€â”€ compliance_checklists.json
â”‚   â”œâ”€â”€ incidents.json
â”‚   â”œâ”€â”€ customer_feedback.json
â”‚   â”œâ”€â”€ regional_kpis.json
â”‚   â”œâ”€â”€ maintenance_requests.json
â”‚   â”œâ”€â”€ promotions.json
â”‚   â”œâ”€â”€ shift_handovers.json
â”‚   â””â”€â”€ daily_sales.json
â”œâ”€â”€ branding/
â”‚   â””â”€â”€ costa_theme.py            # Centralised branding constants (colours, fonts, icon mappings)
â”œâ”€â”€ Dockerfile
â”œâ”€â”€ requirements.txt
â”œâ”€â”€ deploy.sh                     # 1-click Azure Container Apps deployment
â””â”€â”€ README.md
```

---

## Costa Coffee Branding Specification

All widgets MUST use these branding constants consistently. Centralise in `branding/costa_theme.py` and inject into all widget templates.

### Colours

| Token                  | Hex       | Usage                                                  |
|------------------------|-----------|--------------------------------------------------------|
| `--costa-maroon`       | `#6B1C23` | Primary brand colour â€” headers, nav bars, CTAs         |
| `--costa-red`          | `#A4243B` | Secondary accent â€” alerts, important badges            |
| `--costa-cream`        | `#F5F0E8` | Background â€” widget body, cards                        |
| `--costa-gold`         | `#C8A951` | Highlight â€” stars, awards, premium indicators          |
| `--costa-espresso`     | `#2C1810` | Text primary â€” body text, headings                     |
| `--costa-latte`        | `#E8DCC8` | Surface â€” card backgrounds, table alternating rows     |
| `--costa-white`        | `#FFFFFF` | Clean backgrounds, contrast areas                      |
| `--costa-steam`        | `#D4CBC0` | Borders, dividers, subtle UI elements                  |
| `--costa-success`      | `#2E7D32` | Green â€” positive KPIs, completed tasks, in-stock       |
| `--costa-warning`      | `#F57C00` | Amber â€” low stock, approaching targets                 |
| `--costa-danger`       | `#C62828` | Red â€” critical alerts, overdue, out-of-stock           |

### Typography

```css
--costa-font-heading: 'Poppins', 'Segoe UI', system-ui, sans-serif;
--costa-font-body: 'Inter', 'Segoe UI', system-ui, sans-serif;
--costa-font-mono: 'JetBrains Mono', 'Cascadia Code', monospace;
```

Load Poppins (600, 700) and Inter (400, 500, 600) from Google Fonts in the base template.

### Icons

Use **Lucide Icons** (via CDN) throughout. Map each domain to a consistent icon:

| Domain             | Icon              | Usage Context                          |
|--------------------|-------------------|----------------------------------------|
| Dashboard          | `coffee`          | Store daily performance                |
| Rota / Schedule    | `calendar-clock`  | Shift schedules and staffing           |
| Stock / Inventory  | `package`         | Stock levels and orders                |
| Recipes            | `chef-hat`        | Drink and food recipes                 |
| Training           | `graduation-cap`  | Learning modules and progress          |
| Compliance         | `shield-check`    | Food safety and hygiene checklists     |
| Incidents          | `alert-triangle`  | Incident reporting and log             |
| Feedback           | `message-circle`  | Customer NPS and reviews               |
| Regional           | `map-pin`         | Multi-store benchmarks                 |
| Maintenance        | `wrench`          | Equipment maintenance and requests     |
| Promotions         | `megaphone`       | Seasonal menu and campaigns            |
| Shift Handover     | `arrow-right-left`| Shift handover notes                   |
| Maximise           | `maximize-2`      | Full-screen toggle (top-right)         |
| Minimise           | `minimize-2`      | Exit full-screen (top-right)           |

### Widget Design Language

- **Card-based layout**: Each widget is a card with rounded corners (`border-radius: 12px`), subtle shadow (`box-shadow: 0 2px 12px rgba(44,24,16,0.08)`)
- **Header bar**: `--costa-maroon` background, white text, Lucide icon left-aligned, maximise icon right-aligned
- **Status pills**: Small rounded badges using success/warning/danger colours
- **Tables**: Alternating row colours using `--costa-cream` and `--costa-white`, `--costa-maroon` header row
- **Charts**: Use Chart.js (via CDN) with Costa colour palette
- **Animations**: Subtle CSS transitions on hover states and card entry (fade-in-up, 200ms ease)
- **Responsive**: Widgets must work at both inline (400px wide) and full-screen sizes
- **Dark mode**: NOT required for this demo â€” Costa branding is warm/light

---

## Base Widget Template (`widgets/base.html`)

Every widget extends this base template. It MUST include:

### 1. Costa Branding CSS Variables

Inject all colour tokens, fonts, and spacing as CSS custom properties in a `<style>` block in `<head>`.

### 2. Google Fonts + Lucide Icons CDN

```html
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@600;700&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<script src="https://unpkg.com/lucide@latest/dist/umd/lucide.min.js"></script>
```

### 3. OpenAI Apps SDK Full-Screen Maximise

Each widget MUST include the OpenAI Apps SDK script and implement a maximise/minimise toggle icon in the top-right corner of the widget header bar.

```html
<script src="https://cdn.openai.com/apps-sdk/v0/openai-apps-sdk.min.js"></script>
<script>
  const sdk = window.OpenAIAppsSdk;
  let isMaximised = false;
  const maximiseBtn = document.getElementById('maximise-toggle');

  maximiseBtn.addEventListener('click', () => {
    if (isMaximised) {
      sdk.resize({ width: 'compact', height: 'compact' });
      maximiseBtn.setAttribute('data-lucide', 'maximize-2');
    } else {
      sdk.resize({ width: 'full', height: 'full' });
      maximiseBtn.setAttribute('data-lucide', 'minimize-2');
    }
    isMaximised = !isMaximised;
    lucide.createIcons();
  });
</script>
```

The header bar HTML pattern for every widget:

```html
<div class="widget-header">
  <div class="widget-header-left">
    <i data-lucide="{domain_icon}" class="widget-icon"></i>
    <h2 class="widget-title">{Widget Title}</h2>
  </div>
  <button id="maximise-toggle" class="maximise-btn" title="Toggle full screen">
    <i data-lucide="maximize-2"></i>
  </button>
</div>
```

### 4. Initialise Lucide Icons

At the bottom of every widget `<body>`:

```html
<script>lucide.createIcons();</script>
```

---

## MCP Server Implementation (`server.py`)

### FastMCP Server Setup

```python
from fastmcp import FastMCP

mcp = FastMCP(
    name="Costa Coffee Frontline Agent",
    instructions="""You are the Costa Coffee AI Assistant for frontline employees.
    You help baristas, shift managers, store managers, and regional/area managers
    with daily operations including schedules, stock, compliance, training,
    customer feedback, and performance dashboards.
    Always be friendly, practical, and action-oriented.
    When showing data, prefer using the UI widgets for rich visual display.
    Address users by their role context. Use Costa Coffee terminology
    (e.g., 'Barista Maestro' for senior baristas, 'store' not 'branch')."""
)
```

### Resource and Tool Pattern

For EVERY tool that has a corresponding UI widget, implement the following pattern:

#### 1. Register the Widget as an MCP Resource

Each widget resource MUST be registered under the `ui/widget/` URI path with:
- `uri`: `ui/widget/{widget_name}`
- `name`: Human-readable widget name
- `mimeType`: `"text/html+skybridge"`
- `annotations`: `{"readOnlyHint": True}`

```python
@mcp.resource(
    uri="ui/widget/daily_dashboard",
    name="Daily Store Dashboard",
    mime_type="text/html+skybridge",
    annotations={"readOnlyHint": True}
)
async def daily_dashboard_widget(store_id: str = "GLD001") -> str:
    """Renders the daily store performance dashboard widget for the given store."""
    data = load_json("daily_sales.json", store_id)
    return render_widget("dashboard.html", data=data, store_id=store_id)
```

#### 2. Register the Corresponding Tool with `_meta` Pointing to Widget

Each tool that has a UI widget MUST include a `_meta` field in its return value that references the widget resource URI. The tool return type should be a dict with both the structured data AND the `_meta` pointer.

```python
@mcp.tool()
async def get_daily_dashboard(store_id: str = "GLD001") -> dict:
    """Get today's store performance dashboard including sales, footfall,
    average transaction value, and target progress for a Costa Coffee store.

    Args:
        store_id: The store identifier (e.g., 'GLD001' for Guildford High Street)
    """
    data = load_json("daily_sales.json", store_id)
    return {
        "data": data,
        "_meta": {
            "ui": {
                "widget": "ui/widget/daily_dashboard",
                "params": {"store_id": store_id}
            }
        }
    }
```

This pattern MUST be followed for ALL 12 tool/widget pairs. The `_meta.ui.widget` value MUST exactly match the resource URI registered for that widget.

### Helper Functions

Implement these shared helpers in `server.py` or a `utils.py`:

```python
import json
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

DATA_DIR = Path(__file__).parent / "data"
WIDGET_DIR = Path(__file__).parent / "widgets"

jinja_env = Environment(loader=FileSystemLoader(WIDGET_DIR))

def load_json(filename: str, filter_key: str = None, filter_value: str = None) -> dict | list:
    """Load JSON data file, optionally filtering by a key-value pair."""
    with open(DATA_DIR / filename) as f:
        data = json.load(f)
    if filter_key and filter_value:
        if isinstance(data, list):
            return [item for item in data if item.get(filter_key) == filter_value]
        elif isinstance(data, dict) and filter_value in data:
            return data[filter_value]
    return data

def render_widget(template_name: str, **context) -> str:
    """Render an HTML widget template with Costa branding and context data."""
    from branding.costa_theme import THEME
    template = jinja_env.get_template(template_name)
    return template.render(theme=THEME, **context)
```

---

## Tools & Widgets Specification

### Tool 1: Daily Store Dashboard

| Property    | Value |
|-------------|-------|
| Tool        | `get_daily_dashboard(store_id: str)` |
| Resource    | `ui/widget/daily_dashboard` |
| Widget      | `dashboard.html` |
| Data File   | `daily_sales.json` |
| Icon        | `coffee` |

**Widget Content**:
- Hero KPI cards row: Total Sales (GBP), Transactions Count, Average Transaction Value (GBP), Footfall
- Each KPI shows value, delta vs yesterday, and progress bar vs daily target
- Sales by hour bar chart (Chart.js) â€” highlights peak hours
- Top 5 selling products list with units sold
- Staff on shift count badge
- Weather indicator (from data) â€” affects footfall prediction

**Data File** (`daily_sales.json`): Generate data for 5 Costa Coffee stores across 30 days. Each day has hourly breakdowns (6am-9pm). Include realistic Costa Coffee sales patterns (morning rush 7-9am, lunch 12-1pm, afternoon slump 2-3pm, school run 3:30pm). Daily totals should be GBP2,500-GBP4,500 for high street stores. Include product-level sales (Flat White, Latte, Americano, Cappuccino, Hot Chocolate, Iced Latte, Caramel Latte, Chai Latte, Toasties, Paninis, Pastries, Cookies, Meal Deals).

---

### Tool 2: Shift Rota

| Property    | Value |
|-------------|-------|
| Tool        | `get_shift_rota(store_id: str, date: str = "today")` |
| Resource    | `ui/widget/shift_rota` |
| Widget      | `rota.html` |
| Data File   | `rotas.json` |
| Icon        | `calendar-clock` |

**Widget Content**:
- Week view grid: rows = employees, columns = days, cells = shift times (colour-coded by shift type: Open/Mid/Close)
- Today column highlighted with `--costa-gold` border
- Shift type legend
- Staff count per shift summary bar
- Overtime hours flagged in `--costa-warning`
- "Unfilled shifts" alert banner if any gaps exist

**Data File** (`rotas.json`): Generate 4 weeks of rotas for 5 stores, each with 8-15 employees. Shift types: Early (5:30am-1:30pm), Mid (9am-5pm), Late (1pm-9:30pm), Split. Include realistic patterns â€” some staff part-time (students working evenings/weekends), full-time staff rotating. Include 2-3 unfilled shifts per week to demo the alert. Employee names should be realistic UK names.

---

### Tool 3: Stock Levels

| Property    | Value |
|-------------|-------|
| Tool        | `get_stock_levels(store_id: str, category: str = "all")` |
| Resource    | `ui/widget/stock_levels` |
| Widget      | `stock.html` |
| Data File   | `stock.json` |
| Icon        | `package` |

**Widget Content**:
- Category filter tabs: Coffee Beans, Milk & Dairy, Syrups, Food, Cups & Lids, Cleaning
- Table: Item, Current Stock, Par Level, Status (pill: In Stock / Low / Critical / Out), Days Until Reorder, Last Delivery Date
- Critical items highlighted with red left-border
- Doughnut chart showing stock health distribution (% in stock / low / critical)
- "Auto-order suggested" banner for items below reorder point

**Data File** (`stock.json`): Generate 60+ stock items across all categories for 5 stores. Include realistic Costa Coffee supply chain items (Costa Signature Blend beans, Mocha Italia beans, semi-skimmed/oat/soya/coconut milk, vanilla/caramel/hazelnut syrups, panini fillings, pastries with expiry dates, 8oz/12oz/16oz cups, flat lids, domed lids, wooden stirrers, napkins, sanitiser, milk thermometers). Some items should be critically low or out of stock.

---

### Tool 4: Drink & Food Recipes

| Property    | Value |
|-------------|-------|
| Tool        | `get_recipe(item_name: str)` |
| Resource    | `ui/widget/recipe_card` |
| Widget      | `recipe_card.html` |
| Data File   | `recipes.json` |
| Icon        | `chef-hat` |

**Widget Content**:
- Recipe card layout: Item name, category badge (Hot/Iced/Food), allergen icons
- Ingredients list with exact measurements (shots, ml, grams)
- Step-by-step preparation instructions (numbered)
- Size variants (Primo/Medio/Massimo) with different measurements
- Allergen information grid (Milk, Gluten, Nuts, Soya, Egg) with check/cross
- Nutritional info (kcal, sugar) per size
- "Barista Tip" callout box with `--costa-gold` border

**Data File** (`recipes.json`): Generate 35+ recipes covering Costa Coffee's actual menu categories: Espresso-based (Flat White, Latte, Cappuccino, Americano, Cortado, Mocha), Iced (Iced Latte, Iced Cappuccino, Frostino), Hot Chocolate variants, Chai, Teas, Fruit Coolers, and Food items (All Day Breakfast Toastie, Mac & Cheese Toastie, Ham & Cheese Toastie, British Chicken Bacon, Croissants, Cookies, Cake slices). Include proper Costa sizing (Primo/Medio/Massimo), shot counts, milk volumes, and realistic allergen data.

---

### Tool 5: Training Modules

| Property    | Value |
|-------------|-------|
| Tool        | `get_training_progress(employee_id: str = None, store_id: str = "GLD001")` |
| Resource    | `ui/widget/training_progress` |
| Widget      | `training.html` |
| Data File   | `training_modules.json`, `training_progress.json` |
| Icon        | `graduation-cap` |

**Widget Content**:
- If employee_id provided: Individual progress view â€” circular progress ring (overall %), module list with completion status, due dates, overdue items flagged
- If store_id only: Team overview â€” table of all staff with overall progress %, modules due this week count, "Needs Attention" flag
- Module categories: Onboarding, Coffee Mastery, Food Safety (Level 2), Allergen Awareness, Customer Service, Till Operations, Opening/Closing Procedures, Barista Maestro Certification, Fire Safety, First Aid
- Progress bars per module with Costa colour gradient (maroon to gold at 100%)
- "Overdue" badge animation (gentle pulse) for attention

**Data Files**: Generate 12 training modules with descriptions, estimated durations (15min-2hrs), and prerequisites. Generate progress data for all employees across all stores â€” some 100% complete, some in-progress, some overdue. New starters should have more incomplete modules.

---

### Tool 6: Compliance Checklists

| Property    | Value |
|-------------|-------|
| Tool        | `get_compliance_checklist(store_id: str, checklist_type: str = "daily_opening")` |
| Resource    | `ui/widget/compliance_checklist` |
| Widget      | `compliance_checklist.html` |
| Data File   | `compliance_checklists.json` |
| Icon        | `shield-check` |

**Widget Content**:
- Checklist type selector: Daily Opening, Daily Closing, Weekly Deep Clean, Monthly Equipment, Food Safety Audit
- Interactive checklist (display only in widget â€” readOnlyHint) showing items with completed/pending/failed status
- Completion percentage progress bar
- Signoff section: Completed by, Signed off by (manager), Date/Time
- "Critical items" section at top for items that must never be skipped (e.g., temperature checks)
- Historical completion rate sparkline (last 14 days)

**Data File**: Generate 5 checklist types, each with 10-25 items. Items should be realistic Costa Coffee operations: fridge temperature checks (must be 1-5C), milk date checks, sanitiser stations stocked, coffee machine backflush, grinder calibration, display case temperature, handwash stations, floor cleaning, toilet checks, fire exit clear, till float counted, etc. Generate 30 days of historical completion data per store.

---

### Tool 7: Incident Log

| Property    | Value |
|-------------|-------|
| Tool        | `get_incidents(store_id: str, days: int = 7)` |
| Resource    | `ui/widget/incident_log` |
| Widget      | `incident_log.html` |
| Data File   | `incidents.json` |
| Icon        | `alert-triangle` |

**Also create a submission tool (no widget needed)**:

```python
@mcp.tool()
async def submit_incident(store_id: str, category: str, severity: str, description: str, reported_by: str) -> dict:
    """Submit a new incident report for a Costa Coffee store."""
```

**Widget Content**:
- Incident cards in reverse chronological order
- Each card: Severity badge (Low/Medium/High/Critical), Category icon, Date/Time, Description, Reported by, Status (Open/Investigating/Resolved/Closed)
- Filter bar: by severity, category, status
- Category types: Slip/Trip/Fall, Equipment Failure, Customer Complaint, Food Safety, Security, Staff Injury, Property Damage
- Summary stats bar: Open count, Avg resolution time, Incidents this week vs last

**Data File**: Generate 40+ incidents across 5 stores over 90 days. Include realistic scenarios: coffee machine breakdown, customer slip on wet floor, fridge temperature exceedance, till discrepancy, aggressive customer, delivery driver damage, broken chair, pest sighting, staff burn from steam wand, power outage. Vary severities and resolution times.

---

### Tool 8: Customer Feedback

| Property    | Value |
|-------------|-------|
| Tool        | `get_customer_feedback(store_id: str, days: int = 30)` |
| Resource    | `ui/widget/customer_feedback` |
| Widget      | `feedback.html` |
| Data File   | `customer_feedback.json` |
| Icon        | `message-circle` |

**Widget Content**:
- NPS score hero number with gauge visualisation (0-100)
- NPS trend line chart (last 12 weeks)
- Sentiment breakdown: Promoters / Passives / Detractors (stacked bar)
- Word cloud of common themes (CSS-based, not image)
- Recent reviews list: Star rating (1-5, using `--costa-gold` filled stars), comment text, date, source (Google/TripAdvisor/Costa App/In-Store)
- "Action needed" flag on reviews with 1-2 stars that haven't been responded to

**Data File**: Generate 200+ feedback entries per store over 90 days. Include realistic Costa Coffee reviews: praise for coffee quality, complaints about wait times during rush, comments on cleanliness, staff friendliness, loyalty card issues, mobile order problems, seating availability. NPS should vary by store (range 45-72). Include source distribution.

---

### Tool 9: Regional Benchmarks

| Property    | Value |
|-------------|-------|
| Tool        | `get_regional_benchmarks(region: str = "South East")` |
| Resource    | `ui/widget/regional_benchmarks` |
| Widget      | `regional_benchmarks.html` |
| Data File   | `regional_kpis.json` |
| Icon        | `map-pin` |

**Widget Content**:
- Store comparison table: Store Name, Weekly Sales (GBP), Transactions, Avg Transaction (GBP), NPS, Staff Turnover %, Compliance Score %, Rank
- Sortable columns (click header to sort)
- Top performer highlighted with `--costa-gold` row
- Bottom performer flagged with `--costa-warning` row
- KPI radar chart comparing selected store vs regional average (Chart.js)
- Trend arrows on each metric (vs previous week)

**Data File**: Generate 5 regions (South East, London, South West, Midlands, North). Each region has 8-12 stores. Generate 12 weeks of weekly KPI data per store. Include realistic variation â€” high street stores outperform retail park stores, seasonal patterns (summer = more iced drinks, winter = more hot chocolate).

**Stores to include** (sample â€” generate full list):
- GLD001: Guildford High Street
- GLD002: Guildford Station
- RDG001: Reading Oracle
- RDG002: Reading Station
- BAS001: Basingstoke Festival Place
- WOK001: Woking Town Centre
- WIN001: Winchester High Street
- FAR001: Farnham Downing Street
- CRW001: Crawley County Mall
- BRI001: Brighton North Street

---

### Tool 10: Maintenance Requests

| Property    | Value |
|-------------|-------|
| Tool        | `get_maintenance_requests(store_id: str, status: str = "all")` |
| Resource    | `ui/widget/maintenance_requests` |
| Widget      | `maintenance.html` |
| Data File   | `maintenance_requests.json` |
| Icon        | `wrench` |

**Widget Content**:
- Kanban-style columns: Submitted > Scheduled > In Progress > Completed
- Each card: Equipment name, Issue description, Priority badge, Submitted date, Assigned engineer, ETA
- Equipment categories: Coffee Machine (La Cimbali), Grinder, Fridge, Freezer, Oven, Dishwasher, HVAC, Plumbing, Electrical, Signage
- Overdue items pulse animation
- Monthly maintenance cost summary bar

**Data File**: Generate 30+ maintenance requests across stores over 60 days. Include realistic items: La Cimbali M100 group head leak, Mazzer grinder burr replacement, walk-in fridge compressor fault, oven element failure, dishwasher drainage blockage, air conditioning unit servicing, broken front door closer, flickering LED panel. Include engineer names and realistic response/completion times.

---

### Tool 11: Promotions & Seasonal Menu

| Property    | Value |
|-------------|-------|
| Tool        | `get_current_promotions(store_id: str = None)` |
| Resource    | `ui/widget/promotions` |
| Widget      | `promotions.html` |
| Data File   | `promotions.json` |
| Icon        | `megaphone` |

**Widget Content**:
- Active promotions carousel/cards: Promotion name, date range, description, applicable products, discount type
- Seasonal menu spotlight section with item cards (image placeholder, name, price, availability badge)
- Loyalty programme stats: Costa Club points multiplier events
- Upcoming promotions timeline (next 30 days)
- POS code reference table for each promotion (for till entry)

**Data File**: Generate 8-10 promotions including: Costa Club double points week, seasonal drinks (e.g., Toffee Penny Latte, Gingerbread Latte for winter; Tropical Frostino for summer), meal deal offers (any hot drink + toastie for GBP5.50), NHS/Blue Light Card 20% discount, student discount (10% with valid NUS), Happy Hour (buy one get one half price 2-5pm), new product launch (Pistachio Iced Latte), and a charity tie-in (Costa Foundation â€” 10p per drink donated). Include POS codes.

---

### Tool 12: Shift Handover

| Property    | Value |
|-------------|-------|
| Tool        | `get_shift_handover(store_id: str, shift_date: str = "today", shift_type: str = "current")` |
| Resource    | `ui/widget/shift_handover` |
| Widget      | `shift_handover.html` |
| Data File   | `shift_handovers.json` |
| Icon        | `arrow-right-left` |

**Also create a submission tool**:

```python
@mcp.tool()
async def submit_shift_handover(store_id: str, outgoing_shift: str, notes: str, issues: list[str], till_reading: float, stock_alerts: list[str]) -> dict:
    """Submit shift handover notes for the incoming team."""
```

**Widget Content**:
- Handover note card: Outgoing shift manager name, shift time, handover time
- Sections: Key Issues / Carry Forward, Till Reading (GBP), Stock Alerts, Customer Issues, Equipment Status, Staff Notes
- Traffic light status indicators per section
- Previous 3 handovers collapsible for context

**Data File**: Generate 60+ shift handover records across stores. Include realistic notes: "La Cimbali machine 2 running slow â€” engineer booked for tomorrow AM", "Oat milk delivery didn't arrive, using emergency stock from Reading store", "Customer complained about loyalty card â€” escalated to area manager", "New starter Priya shadowing on close tonight â€” needs till training sign-off", "Deep clean of ice machine completed during mid-shift quiet period".

---



---

### Tool 13: Weather Forecast

| Property    | Value |
|-------------|-------|
| Tool        | `get_weather_forecast(store_id: str, days: int = 3)` |
| Resource    | `ui://widget/weather.html` |
| Widget      | `weather.html` |
| Data File   | `weather.json` |
| Icon        | `cloud-sun` |

**Widget Content**:
- Current conditions hero: temperature, feels-like, condition icon (emoji), humidity, wind, precipitation
- Footfall impact badge: % above/below normal with colour coding (green=higher, red=lower)
- Drink demand adjustments grid: hot drinks, iced drinks, hot chocolate, pastries vs. baseline
- Agent tip callout box with weather-specific operational advice
- 5-day forecast cards: condition icon, high/low temp, rain chance, footfall impact delta
- Hourly today strip: scrollable horizontal timeline of condition + temp + rain chance

**Data File** (`weather.json`): Generate realistic UK weather for all 5 stores. Include rain/overcast/sunny conditions. Each store has `current` (with footfall_impact, footfall_impact_pct, drink_demand adjustments, agent_tip) and `forecast` (5 days) and `hourly_today` (6am–9pm). Station stores (GLD002) should show positive footfall impact in wet weather. High-street stores (GLD001) show negative impact.

---

### Tool 14: Travel & Footfall Intel

| Property    | Value |
|-------------|-------|
| Tool        | `get_travel_updates(store_id: str)` |
| Resource    | `ui://widget/travel_updates.html` |
| Widget      | `travel_updates.html` |
| Data File   | `travel_updates.json` |
| Icon        | `map-pin` |

**Widget Content**:
- Disruption summary banner: active/resolving/clear status with severity colour
- Disruption cards: transport type icon, title, description, affected routes, severity pill, status pill, start–end times, footfall impact %, footfall note
- Local events cards: event name, date, type icon, location + distance, expected attendance, footfall opportunity rating, opportunity note (with gold border for high-opportunity, red for competitive risk)
- Footfall forecast by period: morning rush / late morning / lunch / afternoon / evening — horizontal bar chart showing % vs normal with explanatory notes

**Data File** (`travel_updates.json`): Generate for 5 stores. Include realistic disruptions: South Western Railway signal failure (GLD001 — negative, GLD002 — positive since stranded commuters visit), bus diversions, road closures. Include local events: Christmas market outside GLD001 (+25-30% footfall), Reading FC match near RDG001 (+40% evening), Brighton food festival near BRI001, Pret a Manger competitor opening near BRI001 (risk). Include structured `footfall_forecast` by time period.

---

### Tool 15: Social Media & Reputation

| Property    | Value |
|-------------|-------|
| Tool        | `get_social_media_mentions(store_id: str, days: int = 7)` |
| Resource    | `ui://widget/social_media.html` |
| Widget      | `social_media.html` |
| Data File   | `social_media.json` |
| Icon        | `share-2` |

**Widget Content**:
- Urgent alerts banner: influencer visits requiring immediate action (high-urgency)
- Unanswered review warning banner
- Sentiment KPI cards: overall score (/5), positive %, negative %, total mentions (7d) with vs-last-week delta
- Sentiment breakdown bar: green/grey/red proportional bar
- Trending hashtags: colour-coded by sentiment (green=positive, red=negative, blue=neutral) with mention count
- Influencer alerts cards: platform avatar, username, followers, post excerpt, reach estimate, engagement rate, recommended action box, urgency badge
- Recent mentions scroll list: platform avatar, username, followers, star rating (if applicable), content, sentiment pill, "Response Overdue" pulsing badge if applicable, theme tags

**Data File** (`social_media.json`): Generate for 5 stores. GLD001: positive sentiment, @GuildfordFoodie (12K Instagram) visiting today, @SurreyLiving article, one overdue 1-star review about wait times. GLD002: mixed, disruption-day tweets. BRI001: trending down, @BrightonBites TikToker (45K) doing competitive review ahead of Pret opening, two negative reviews mentioning burnt coffee. Include `response_templates` for common negative themes. Include `influencer_alerts` with `urgency: high` for urgent cases.


## Demo Storyline

### "A Day at Costa Coffee Guildford High Street"

The demo follows **Sam**, a Shift Manager at Costa Coffee Guildford High Street (GLD001), through a typical day. The AI agent is accessed via Microsoft Copilot on a tablet mounted near the back-of-house area. The agent has access to:

- **This MCP server** — tools and widgets for store operations
- **SharePoint** — Costa policy documents, seasonal playbooks, VM standards, allergen updates, area manager visit agendas, HR guides, and training materials
- **Web search** — local events, competitor activity, FSA guidance, travel news
- **Image understanding** — Sam can upload photos (stock room, damaged equipment, incidents, displays) and the agent analyses them

> **Why is this better than a dedicated mobile app?**
> The power is in the *connections the agent makes across multiple data sources in real time* — things no single-purpose app could do. A mobile app shows you your rota. The agent reads your rota, crosses it with today's weather and a train disruption, finds a gap in your staffing, checks the Costa Peak Staffing Playbook on SharePoint, and tells you exactly what to do — before you even thought to ask.

---

#### Scene 1: Morning Open (6:00 AM)
> **Sam**: "Good morning! What do I need to know for today's open?"

**Agent synthesises five sources simultaneously:**

1. **`get_shift_handover`** → Shift handover widget: La Cimbali machine 2 running slow (engineer booked for 10am), oat milk delivery did not arrive yesterday — using emergency stock
2. **`get_shift_rota`** → Rota widget: full team in today, but Marcus is on leave — one barista short for the lunch rush
3. **`get_compliance_checklist`** → Compliance widget: daily opening checklist ready — temperature logs due
4. **`get_weather_forecast`** → **Weather widget**: Heavy rain all day — footfall down 18% predicted, hot drink demand up 25%, hot chocolate up 35%
5. **`get_travel_updates`** → **Travel updates widget**: Signal failure on South Western Railway — Guildford line running 25-40 mins late. Disruption expected to clear by 09:30. Morning commuter rush will be suppressed until then, but pent-up demand from 09:30-11:00.

**Agent's joined-up insight** (not possible with any single app):
> "Morning, Sam! Heavy rain and a signal failure means your 7-9am rush will be about 30% lighter than usual — but when the trains start running again around 09:30, expect a wave of cold, wet commuters. I'd push your coffee prep back 30 minutes and focus on hot drinks. The Toffee Penny Latte is performing really well in wet weather — worth moving it to the front display. Also — your oat milk is critically low from yesterday's delivery miss. Shall I check stock levels now?"

**Why this is agent magic**: No app correlates weather + train disruptions + stock + rota + the handover from last night and gives you an integrated action plan. The agent does it in one message.

---

#### Scene 2: Influencer Alert (7:15 AM)
> **Agent proactively**: "Sam, quick heads-up — @GuildfordFoodie (12,400 Instagram followers) just posted from your store. They've tagged Costa and mentioned the Toffee Penny Latte. Their reviews typically reach 18,000+ people. I'd recommend the team know they may be being featured today."

**`get_social_media_mentions`** → **Social media widget** shows:
- @GuildfordFoodie post (positive, 4.8% engagement rate)
- @SurreyLiving Magazine teasing a "Best Coffee in Guildford" article
- One overdue 1-star review from yesterday (15-minute wait at lunchtime) that has not been responded to
- Sentiment score: 4.3/5, trending up

**Agent's action**:
> "The 1-star review from James K. yesterday is flagged as overdue — it has been sitting 18 hours. Want me to draft a response? I have a response template from the Costa Customer Care Playbook on SharePoint that fits this situation perfectly."

Sam says yes. Agent drafts a personalised response in Costa's brand voice, ready for Sam to approve.

**Why this is agent magic**: A reviews app just shows you the review. The agent reads it, checks SharePoint for the correct response template, drafts the reply, and flags that it has been sitting unanswered — without being asked.

---

#### Scene 3: Stock Issue — With Image Grounding (8:30 AM)
> **Sam** *[uploads a photo of the stock room]*: "Can you check what's going on in here?"

**Agent analyses the image**:
> "I can see from the photo that your oat milk is down to approximately 2-3 cartons — that matches the system showing Critical status. I also notice the cleaning products are stored on the same shelf as the Mocha Italia beans — that is a food safety violation under Costa's Food Safety Standards on SharePoint. The beans need to be at least 2 metres from cleaning chemicals.
>
> I've logged a compliance note for the storage issue, and I'm pulling up your full stock levels now."

**`get_stock_levels`** → Stock widget: Oat milk Critical (2 cartons), semi-skimmed OK, soya Low.

**Agent continues**:
> "Guildford Station (GLD002) shows surplus oat milk — they received a double delivery yesterday. Want me to draft a transfer request?"

**Why this is agent magic**: No mobile app can look at a photo, identify both a stock issue AND a compliance violation, cross-reference store policy from SharePoint, and then pull the relevant widget — all in one response to a photo.

---

#### Scene 4: Recipe + Allergen Deep Dive (10:00 AM)
> **Sam**: "New barista Priya is asking about the Pistachio Iced Latte — she's not sure if it contains peanuts."

**`get_recipe`** → Recipe card widget for Pistachio Iced Latte with full allergen grid.

**Agent**:
> "Good catch. The Pistachio Iced Latte uses pistachio syrup — that is a tree nut allergen, not peanut. However, I also did a web search for FSA updates on pistachio allergen labelling — there was a guidance update in October 2024 requiring more prominent labelling for tree nuts.
>
> I found the updated allergen briefing on SharePoint. Priya's allergen awareness training was last completed 14 months ago — the new FSA guidance recommends annual refreshers. Want me to pull up the training module and schedule her refresher?"

**Why this is agent magic**: The agent connected a recipe question to a live web search for regulatory updates, a SharePoint document, an employee training record, and a recommended action. A recipe app just shows you the recipe.

---

#### Scene 5: Proactive Footfall Management (11:30 AM)
> **Agent proactively**: "The signal failure has cleared — trains are running again. Based on historical patterns, expect a delayed lunch rush starting around 12:15. The Christmas market outside is picking up — footfall tracking 25% above your typical Tuesday lunch. You're on course to beat yesterday's sales target."

**`get_daily_dashboard`** → Dashboard widget: sales 8% above target by 11:30am.

**Agent**:
> "The rain is actually working in your favour today — people are seeking shelter and the Christmas market is bringing in visitors. Hot chocolate sales are up 38% vs yesterday. The Costa Seasonal Merchandising Playbook on SharePoint recommends moving the Festive Bundle to front-of-counter on rainy high-street days."

---

#### Scene 6: Incident — With Image (12:30 PM)
> **Sam**: "A customer just slipped near the entrance — floor was wet from the rain." *[uploads photo of wet entrance area]*

**Agent**:
> "I can see from the photo this is the main entrance mat area — high risk zone in wet weather. I'm logging this as a Slip/Trip/Fall incident. The photo shows no wet floor sign visible. I'll note that in the incident log."

**`submit_incident`** → Incident INC-0247 logged: Slip/Trip/Fall, Medium severity, GLD001, 12:32pm.

**Agent**:
> "Done. I've added a reminder: your incident protocol requires a manager countersignature within 2 hours. I'll prompt you at 14:30 if it has not been countersigned. Do you need me to pull the First Aid procedure from SharePoint?"

---

#### Scene 7: Training Gap + Regulatory Update (2:30 PM)
> **Sam**: "It's quiet — who's overdue on training?"

**`get_training_progress`** → Training widget for GLD001: 3 staff overdue on Allergen Awareness, 1 on Food Safety Level 2.

**Agent**:
> "Three staff are overdue on Allergen Awareness. I also did a web search and found the FSA updated their recommendation to annual refreshers — this means 2 more staff who show as current are actually due.
>
> I found the updated training materials on SharePoint. Want me to schedule a refresher for this Thursday at 2pm? I can check the rota to confirm all 5 staff are on shift."

Agent checks the rota, confirms all 5 are on Thursday 2pm, proposes the booking.

**Why this is agent magic**: The training system just shows who is overdue by old rules. The agent searched for a regulatory update, re-evaluated compliance against the new standard, found the updated materials on SharePoint, and checked the rota for a suitable slot — all in one step.

---

#### Scene 8: Area Manager Visit Prep (3:00 PM)
> **Sam**: "Area manager Karen is visiting tomorrow. What do I need to know?"

**Agent searches SharePoint** for Karen's visit agenda:
> "I found Karen's visit agenda on SharePoint. She is focusing on: allergen compliance (training records), waste reduction (you're 12% above regional average), and customer feedback response times. The 1-star review from this morning is now 19 hours old and still unanswered — shall we deal with that before you go home today?"

**`get_regional_benchmarks`** → Regional widget: GLD001 ranked 3rd of 10, strong NPS (67), food waste flagged.

**Agent**:
> "For the waste issue — I found the Costa Waste Reduction Playbook on SharePoint. The quick wins are portion discipline on syrups and the end-of-day pastry markdown protocol. Want me to pull the specific guidance?"

---

#### Scene 9: Social Media and Promotions (4:00 PM)
> **Sam**: "Anything else I should be doing this afternoon?"

**Agent proactively surfaces**:

1. **`get_social_media_mentions`** → @GuildfordFoodie review posted — 4.5 stars, reached 14,000 people. @SurreyLiving article live — Costa GLD001 featured as #2 in Guildford.
2. **`get_customer_feedback`** → NPS up from 62 to 67. "Consistently great" recurring theme.
3. **Agent web search** for "Guildford events this week" — University of Surrey winter exams start Monday.

> "Exam season starts Monday — Surrey students are about 18% of your afternoon customer base. Based on last year's pattern (found in the Regional Performance Archive on SharePoint), exam season drives a 15% uplift in afternoon cafe visits. I'd recommend activating the NUS 10% discount visibility now."

**`get_current_promotions`** → Promotions widget: NUS discount active, Toffee Penny Latte runs to end of month.

---

#### Scene 10: Shift Handover (5:00 PM)
> **Sam**: "I'm heading off — help me do the handover."

**Agent pre-populates the handover** with everything observed today:
> "I've drafted your handover. Key items: La Cimbali machine 2 engineer tomorrow AM, oat milk transfer from GLD002 confirmed for 8am, incident INC-0247 countersigned, @GuildfordFoodie review live (positive — evening team should maintain standards), engineering works on A3 tonight (lower early evening footfall expected), Karen's visit tomorrow (allergen and waste metrics are priority). Anything to add?"

Sam reviews, adds the till reading, and submits.

**`submit_shift_handover`** → Handover logged and visible to the incoming shift manager.

---

#### Scene 11: Area Manager View (Bonus)
> **Regional Manager Karen**: "Give me an overview of my South East stores this week."

**`get_regional_benchmarks`** → Regional widget: all 10 stores ranked.

> **Karen**: "Brighton's NPS has dropped. What's going on there?"

**`get_social_media_mentions`** → BRI001 social widget:
- @BrightonBites TikTok (45K followers) did a comparative review ahead of Pret a Manger opening 180m away
- Two negative Google reviews mentioning "burnt coffee taste"
- Sentiment down 12% vs last week

**Agent**:
> "A new Pret a Manger opens on North Street Monday, 180 metres from BRI001. Two Google reviews mention burnt coffee — the Mazzer grinder burr replacement is overdue by 3 weeks. I'd recommend: (1) log an urgent maintenance request for the grinder, and (2) activate Costa Club double points at BRI001 this week to pre-empt customer trial of the new Pret."

> **Karen** *[uploads a photo of the competitor's new store exterior]*: "This is the Pret — what are we dealing with?"

**Agent analyses the image**:
> "I can see a newly refurbished Pret a Manger with a visible 'Coffee + Sandwich £4.99' promotion in the window. That undercuts our meal deal by 51p. I'd recommend activating the Costa Club double points week at BRI001 immediately — it is already set up in your promotions system. Want me to activate it from here?"

**Why this is agent magic**: A regional dashboard app shows you a KPI drop. The agent connects the KPI drop to social sentiment, a competitor opening, a maintenance issue, and a photo of the competitor's window offer — and proposes a specific counter-promotion, all in one conversation.


## Azure Deployment Script (`deploy.sh`)

Create a **single bash script** that deploys everything to Azure Container Apps with zero pre-existing infrastructure required. The script should:

### Prerequisites Check
- Verify `az` CLI is installed and logged in
- Verify `docker` is available

### Parameters (with defaults)

```bash
RESOURCE_GROUP="${RESOURCE_GROUP:-rg-costa-mcp-demo}"
LOCATION="${LOCATION:-uksouth}"
CONTAINER_APP_NAME="${CONTAINER_APP_NAME:-costa-frontline-mcp}"
CONTAINER_REGISTRY_NAME="${CONTAINER_REGISTRY_NAME:-costamcpregistry}"
CONTAINER_APP_ENV_NAME="${CONTAINER_APP_ENV_NAME:-costa-mcp-env}"
IMAGE_TAG="${IMAGE_TAG:-latest}"
TARGET_PORT=8000
```

### Script Steps

1. **Create Resource Group**
   ```bash
   az group create --name $RESOURCE_GROUP --location $LOCATION
   ```

2. **Create Azure Container Registry**
   ```bash
   az acr create --resource-group $RESOURCE_GROUP --name $CONTAINER_REGISTRY_NAME --sku Basic --admin-enabled true
   ```

3. **Build and Push Docker Image**
   ```bash
   az acr build --registry $CONTAINER_REGISTRY_NAME --image $CONTAINER_APP_NAME:$IMAGE_TAG .
   ```

4. **Create Container Apps Environment**
   ```bash
   az containerapp env create \
     --name $CONTAINER_APP_ENV_NAME \
     --resource-group $RESOURCE_GROUP \
     --location $LOCATION
   ```

5. **Deploy Container App**
   ```bash
   az containerapp create \
     --name $CONTAINER_APP_NAME \
     --resource-group $RESOURCE_GROUP \
     --environment $CONTAINER_APP_ENV_NAME \
     --image "$CONTAINER_REGISTRY_NAME.azurecr.io/$CONTAINER_APP_NAME:$IMAGE_TAG" \
     --registry-server "$CONTAINER_REGISTRY_NAME.azurecr.io" \
     --registry-username $(az acr credential show --name $CONTAINER_REGISTRY_NAME --query username -o tsv) \
     --registry-password $(az acr credential show --name $CONTAINER_REGISTRY_NAME --query passwords[0].value -o tsv) \
     --target-port $TARGET_PORT \
     --ingress external \
     --min-replicas 1 \
     --max-replicas 3 \
     --cpu 0.5 \
     --memory 1.0Gi \
     --env-vars "MCP_TRANSPORT=streamable-http" "MCP_HOST=0.0.0.0" "MCP_PORT=$TARGET_PORT"
   ```

6. **Output the MCP endpoint URL**
   ```bash
   FQDN=$(az containerapp show --name $CONTAINER_APP_NAME --resource-group $RESOURCE_GROUP --query properties.configuration.ingress.fqdn -o tsv)
   echo ""
   echo "=============================================="
   echo "  Costa Coffee MCP Server Deployed!"
   echo "  Endpoint: https://$FQDN/mcp"
   echo "  Transport: Streamable HTTP"
   echo "  Auth: None (demo)"
   echo "=============================================="
   ```

### Dockerfile

```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "server.py"]
```

### requirements.txt

```
fastmcp>=2.0.0
jinja2>=3.1.0
uvicorn>=0.30.0
```

### Server Transport Config

In `server.py`, the server must start with streamable HTTP transport:

```python
if __name__ == "__main__":
    import os
    mcp.run(
        transport="streamable-http",
        host=os.getenv("MCP_HOST", "0.0.0.0"),
        port=int(os.getenv("MCP_PORT", "8000")),
    )
```

---

## Data Generation Rules

When generating JSON data files:

1. **Volume**: Generate realistic volumes. Minimum 100 records for transactional data (sales, feedback, incidents). Minimum 30 days of time-series data.
2. **Consistency**: Employee IDs, store IDs, and product names MUST be consistent across ALL data files. If "Priya Sharma" is employee EMP042 in `employees.json`, she must be EMP042 everywhere.
3. **Realism**: Use realistic UK names, realistic Costa Coffee products and pricing (Flat White Medio = ~GBP3.65), realistic UK addresses, realistic operational patterns.
4. **Store IDs**: Use format `{3-letter city code}{3-digit number}` e.g., GLD001, RDG001, BAS001.
5. **Employee IDs**: Use format `EMP{3-digit number}` starting from EMP001.
6. **Dates**: Centre data around the current date. Historical data going back 90 days, future rotas going forward 14 days.
7. **Edge Cases**: Include some anomalies in data for demo interest: a store with unusually high incidents, a new starter with zero training, a day with abnormally low sales (simulate equipment breakdown), a 5-star review mentioning a specific barista by name.

---

## Quality Checklist

Before considering the project complete, verify:

- [ ] All 12 tools registered with correct signatures and docstrings
- [ ] All 12 widget resources registered at `ui/widget/` path with `text/html+skybridge` mimeType
- [ ] All widget resources have `annotations: {"readOnlyHint": True}`
- [ ] All tools with widgets return `_meta.ui.widget` pointing to correct resource URI
- [ ] `submit_incident` and `submit_shift_handover` tools work (write-back to JSON)
- [ ] All widgets extend `base.html` with Costa branding
- [ ] All widgets have maximise/minimise toggle using OpenAI Apps SDK
- [ ] All widgets use Lucide icons consistently per the icon mapping table
- [ ] All widgets are responsive (400px inline to full-screen)
- [ ] All JSON data files are internally consistent (IDs match across files)
- [ ] `deploy.sh` runs end-to-end with no manual steps
- [ ] `docker build` succeeds locally
- [ ] Server starts and responds on `/mcp` endpoint
- [ ] README.md includes setup instructions, architecture diagram (Mermaid), and demo walkthrough
