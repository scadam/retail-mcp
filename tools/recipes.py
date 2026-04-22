def register_recipes(mcp, load_json, render_widget):
    @mcp.resource("widget://recipe-card", mime_type="text/html+skybridge",
                  annotations={"readOnlyHint": True})
    def recipe_widget() -> str:
        return render_widget("recipe_card.html", recipe={})

    @mcp.tool()
    def get_recipe(item_name: str) -> dict:
        """Get the recipe card for a Costa Coffee menu item."""
        recipes = load_json("recipes.json")
        recipe = next(
            (r for r in recipes if r["name"].lower() == item_name.lower()),
            None
        )
        if not recipe:
            # fuzzy: check if item_name is contained in the name
            recipe = next(
                (r for r in recipes if item_name.lower() in r["name"].lower()),
                None
            )
        if not recipe:
            return {
                "data": {"error": f"Recipe not found for '{item_name}'"},
                "available_recipes": [r["name"] for r in recipes],
                "_meta": {"ui": {"widget": "widget://recipe-card", "html": "", "params": {}}},
            }
        html = render_widget("recipe_card.html", recipe=recipe)
        return {
            "data": recipe,
            "_meta": {
                "ui": {
                    "widget": "widget://recipe-card",
                    "html": html,
                    "params": {"item_name": item_name},
                }
            },
        }
