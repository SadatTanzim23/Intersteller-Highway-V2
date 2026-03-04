"""
Command-line interface: programname startplanet destination rockettype payload ddmmyyyy ddmmyyyy
Returns JSON with Flight impossible, Efficient flight parameters, Soonest arrival flight parameters.
"""
import sys
import json
import trajectory as tr
import ships as sh

# Planet name normalization for CLI
PLANET_ALIASES = {
    "mercury": "Mercury", "venus": "Venus", "earth": "Earth", "mars": "Mars",
    "jupiter": "Jupiter", "saturn": "Saturn", "uranus": "Uranus", "neptune": "Neptune",
    "pluto": "Pluto", "ceres": "Ceres",
}


def normalize_planet(name: str) -> str:
    return PLANET_ALIASES.get(name.strip().lower(), name.strip())


def main(args=None):
    if args is None:
        args = sys.argv[1:]
    if len(args) != 6:
        print(json.dumps({
            "Flight impossible": True,
            "error": "Usage: programname startplanet destination rockettype payload ddmmyyyy ddmmyyyy"
        }, indent=2))
        return 1
    start_planet = normalize_planet(args[0])
    destination = normalize_planet(args[1])
    rocket_type = args[2].strip()
    try:
        payload = float(args[3])
    except ValueError:
        print(json.dumps({"Flight impossible": True, "error": "Invalid payload (must be number)"}, indent=2))
        return 1
    ddmmyyyy_start = args[4].strip()
    ddmmyyyy_end = args[5].strip()
    # Resolve ship name (alias -> canonical)
    ship_name = sh.SHIP_ALIASES.get(rocket_type.lower(), rocket_type)
    if ship_name not in sh.SHIP_SPECS:
        ship_name = rocket_type
    result = tr.compute_both_options(start_planet, destination, ship_name, payload, ddmmyyyy_start, ddmmyyyy_end)
    # Ensure keys match spec exactly
    out = {
        "Flight impossible": result["Flight impossible"],
    }
    if not result["Flight impossible"]:
        ef = result.get("Efficient flight parameters") or {}
        out["Efficient flight parameters"] = {k: v for k, v in ef.items() if not str(k).startswith("_")}
        sf = result.get("Soonest arrival flight parameters") or {}
        out["Soonest arrival flight parameters"] = {k: v for k, v in sf.items() if not str(k).startswith("_")}
    else:
        if "error" in result:
            out["error"] = result["error"]
    print(json.dumps(out, indent=2))
    return 0 if not result["Flight impossible"] else 1


if __name__ == "__main__":
    sys.exit(main())
