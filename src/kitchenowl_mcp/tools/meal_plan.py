import datetime

from .. import state


async def get_meal_plan(start_date: str, end_date: str) -> list[dict]:
    """Get planned meals in a date range.

    Dates must be in YYYY-MM-DD format. Returns all planner entries between
    start_date and end_date inclusive, each with recipe_id, recipe name, and date.
    """
    entries = await state.get_client().get_planner()
    result = []
    for e in entries:
        cooking_date_ms = e.get("cooking_date")
        if isinstance(cooking_date_ms, int) and cooking_date_ms > 0:
            entry_date = datetime.datetime.fromtimestamp(
                cooking_date_ms / 1000, tz=datetime.UTC
            ).strftime("%Y-%m-%d")
        else:
            raw = e.get("date", e.get("day", ""))
            if not isinstance(raw, str):
                continue
            entry_date = raw
        if start_date <= entry_date <= end_date:
            result.append(e)
    return result


async def add_meal_plan_entry(
    recipe_id: int,
    date: str,
    meal_type: str = "dinner",
    servings: int = 4,
) -> dict:
    """Add a recipe to the meal plan on a specific date.

    date must be in YYYY-MM-DD format. meal_type is a label like "breakfast",
    "lunch", or "dinner". servings is the number of people to cook for.
    Returns the created planner entry.
    """
    cooking_dt = datetime.datetime.strptime(date, "%Y-%m-%d").replace(
        tzinfo=datetime.UTC
    )
    payload = {
        "recipe_id": recipe_id,
        "cooking_date": int(cooking_dt.timestamp() * 1000),
        "yields": servings,
    }
    return await state.get_client().add_planner_entry(payload)
