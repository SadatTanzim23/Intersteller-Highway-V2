"""
Orbital data for solar system bodies (planets, Pluto, Ceres).
Used for SOI, parking orbits (12h), and transfer calculations.
Values from standard references (e.g. NASA fact sheets); can be replaced by API.
"""
from math import pi, sqrt

# AU in km, Sun GM in km^3/s^2
AU_KM = 149597870.7
GM_SUN = 1.32712440018e11  # km^3/s^2

# Bodies: semi-major axis (AU), mass (kg), name for display
# Masses from standard planetary fact sheets (order: same as planet_options)
BODIES = {
    "Mercury": {"a_au": 0.387098, "mass_kg": 3.285e23},
    "Venus":   {"a_au": 0.723332, "mass_kg": 4.867e24},
    "Earth":   {"a_au": 1.0,      "mass_kg": 5.972e24},
    "Mars":    {"a_au": 1.52366,  "mass_kg": 6.417e23},
    "Jupiter": {"a_au": 5.20336,  "mass_kg": 1.898e27},
    "Saturn":  {"a_au": 9.53707,  "mass_kg": 5.683e26},
    "Uranus":  {"a_au": 19.1913, "mass_kg": 8.681e25},
    "Neptune": {"a_au": 30.0689, "mass_kg": 1.024e26},
    "Pluto":   {"a_au": 39.482,   "mass_kg": 1.303e22},
    "Ceres":   {"a_au": 2.766,    "mass_kg": 9.38e20},
}
M_SUN = 1.989e30  # kg


def semi_major_axis_km(body: str) -> float:
    """Semi-major axis in km."""
    if body not in BODIES:
        return 1.0 * AU_KM
    return BODIES[body]["a_au"] * AU_KM


def body_mass_kg(body: str) -> float:
    """Body mass in kg."""
    return BODIES.get(body, {}).get("mass_kg", 5.972e24)


def sphere_of_influence_km(body: str) -> float:
    """SOI radius in km: r = a * (m/M)^(2/5)."""
    a = semi_major_axis_km(body)
    m = body_mass_kg(body)
    return a * (m / M_SUN) ** (2.0 / 5.0)


def orbital_period_days(body: str) -> float:
    """Orbital period around Sun in days (Kepler: T^2 proportional to a^3)."""
    a_km = semi_major_axis_km(body)
    T_sec = 2 * pi * sqrt(a_km ** 3 / GM_SUN)
    return T_sec / (24 * 3600)


def gm_body_km3s2(body: str) -> float:
    """Standard gravitational parameter for body (km^3/s^2)."""
    G = 6.67430e-20  # km^3/(kg*s^2)
    return G * body_mass_kg(body)


def parking_orbit_radius_km(body: str, period_hours: float = 12.0) -> float:
    """Radius of circular parking orbit for given period (hours). T = 2*pi*sqrt(r^3/mu) -> r = (mu*T^2/(4*pi^2))^(1/3)."""
    mu = gm_body_km3s2(body)
    T_sec = period_hours * 3600.0
    r = (mu * T_sec * T_sec / (4 * pi * pi)) ** (1.0 / 3.0)
    return r


def parking_orbit_period_hours(body: str, radius_km: float) -> float:
    """Orbital period in hours for circular orbit at radius_km."""
    mu = gm_body_km3s2(body)
    T_sec = 2 * pi * sqrt(radius_km ** 3 / mu)
    return T_sec / 3600.0


def circular_orbital_speed_km_s(mu_km3s2: float, radius_km: float) -> float:
    """Speed in km/s for circular orbit: v = sqrt(mu/r)."""
    return sqrt(mu_km3s2 / radius_km)


def all_bodies():
    """Return list of body names (for refuel stations)."""
    return list(BODIES.keys())
