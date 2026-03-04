"""
Store and retrieve past trade routes for comparison and optimization.
"""
import json
import os
from datetime import datetime

STORAGE_DIR = os.path.join(os.path.dirname(__file__), "route_history")
STORAGE_FILE = os.path.join(STORAGE_DIR, "routes.json")


def _ensure_dir():
    os.makedirs(STORAGE_DIR, exist_ok=True)


def _load_all() -> list:
    _ensure_dir()
    if not os.path.exists(STORAGE_FILE):
        return []
    try:
        with open(STORAGE_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []


def _save_all(routes: list):
    _ensure_dir()
    with open(STORAGE_FILE, "w") as f:
        json.dump(routes, f, indent=2)


def save_route(origin: str, dest: str, ship: str, payload_kg: float,
               window_start: str, window_end: str, result: dict) -> dict:
    """Append a route result to history. Returns the stored entry."""
    entry = {
        "id": datetime.now().isoformat(),
        "origin": origin,
        "destination": dest,
        "ship": ship,
        "payload_kg": payload_kg,
        "window_start": window_start,
        "window_end": window_end,
        "result": result,
    }
    routes = _load_all()
    routes.append(entry)
    _save_all(routes)
    return entry


def get_all_routes() -> list:
    """Return all stored routes (most recent last)."""
    return _load_all()


def get_route_by_id(route_id: str) -> dict | None:
    for r in _load_all():
        if r.get("id") == route_id:
            return r
    return None


def clear_all_routes():
    """Remove all saved routes from history."""
    _save_all([])


def get_routes_filter(origin: str = None, dest: str = None, ship: str = None) -> list:
    """Retrieve past routes matching optional filters."""
    routes = _load_all()
    if origin:
        routes = [r for r in routes if r.get("origin") == origin]
    if dest:
        routes = [r for r in routes if r.get("destination") == dest]
    if ship:
        routes = [r for r in routes if r.get("ship") == ship]
    return routes
