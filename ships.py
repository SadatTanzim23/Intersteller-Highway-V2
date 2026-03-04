"""
ICTB-certified ship specifications (dry mass, fuel capacity, Isp, max payload).
"""
# Ship name (display) -> dry_kg, fuel_capacity_kg, Isp_km_s, fuel_type, max_payload_kg
SHIP_SPECS = {
    "Chevrolet Super Sonic": {
        "dry_mass_kg": 5000,
        "fuel_capacity_kg": 20000,
        "Isp_km_s": 4.2,
        "fuel_type": "Leaded gasoline",
        "max_payload_kg": 1000,
    },
    "The Planet Hopper": {
        "dry_mass_kg": 10000,
        "fuel_capacity_kg": 100000,
        "Isp_km_s": 6.7,
        "fuel_type": "Compressed air",
        "max_payload_kg": 4000,
    },
    "Moonivan": {
        "dry_mass_kg": 25000,
        "fuel_capacity_kg": 400000,
        "Isp_km_s": 9.1,
        "fuel_type": "Biofuel",
        "max_payload_kg": 10000,
    },
    "Blue Origin Delivery Ship": {
        "dry_mass_kg": 69000,
        "fuel_capacity_kg": 800000,
        "Isp_km_s": 15.2,
        "fuel_type": "Whale oil",
        "max_payload_kg": 50000,
    },
    "Yamaha Space Cycle": {
        "dry_mass_kg": 1000,
        "fuel_capacity_kg": 2500,
        "Isp_km_s": 100.0,
        "fuel_type": "Antimatter",
        "max_payload_kg": 100,
    },
    "Ford F-1500": {
        "dry_mass_kg": 10000,
        "fuel_capacity_kg": 100000,
        "Isp_km_s": 18.67,
        "fuel_type": "Space Diesel",
        "max_payload_kg": 8000,
    },
    "Behemoth": {
        "dry_mass_kg": 100000,
        "fuel_capacity_kg": 1500000,
        "Isp_km_s": 11.1,
        "fuel_type": "Nuclear propulsion",
        "max_payload_kg": 100000,
    },
}

# CLI / GUI mapping: short names or alternate spellings -> canonical name
SHIP_ALIASES = {
    "chevrolet super sonic": "Chevrolet Super Sonic",
    "chevrolet": "Chevrolet Super Sonic",
    "planet hopper": "The Planet Hopper",
    "moonivan": "Moonivan",
    "blue origin": "Blue Origin Delivery Ship",
    "blue origin delivery ship": "Blue Origin Delivery Ship",
    "yamaha space cycle": "Yamaha Space Cycle",
    "yamaha": "Yamaha Space Cycle",
    "ford f-1500": "Ford F-1500",
    "ford f1500": "Ford F-1500",
    "ford": "Ford F-1500",
    "behemoth": "Behemoth",
}


def get_ship_spec(ship_name: str) -> dict | None:
    """Return spec dict for ship (by canonical or alias name)."""
    name = ship_name.strip()
    canonical = SHIP_ALIASES.get(name.lower(), name)
    return SHIP_SPECS.get(canonical)


def fuel_required_kg(initial_mass_kg: float, delta_v_km_s: float, Isp_km_s: float) -> float:
    """
    Fuel (kg) needed to achieve delta_v with Isp.
    delta_v = Isp * ln(m0/mf) => mf = m0 * exp(-delta_v/Isp), fuel = m0 - mf.
    """
    if delta_v_km_s <= 0 or Isp_km_s <= 0:
        return 0.0
    mf = initial_mass_kg * __import__("math").exp(-delta_v_km_s / Isp_km_s)
    return initial_mass_kg - mf


def can_carry_payload(ship_name: str, payload_kg: float) -> bool:
    spec = get_ship_spec(ship_name)
    return spec is not None and 0 <= payload_kg <= spec["max_payload_kg"]


def list_ship_names():
    return list(SHIP_SPECS.keys())
