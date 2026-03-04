"""
Trajectory and transfer calculations: positions, delta-V, fuel.
Assumes circular orbits; delta-V in fuel-expenditure terms (rocket equation).
"""
from math import pi, sqrt, cos, sin, atan2, exp
from datetime import datetime, timedelta

import orbital_data as od
import ships as sh

GM_SUN = od.GM_SUN
EPOCH = datetime(2025, 1, 1)  # day 0


def date_to_days(d: datetime) -> float:
    """Days since epoch."""
    return (d - EPOCH).total_seconds() / 86400.0


def days_to_date(day: float) -> datetime:
    return EPOCH + timedelta(days=day)


def parse_ddmmyyyy(s: str) -> datetime | None:
    """Parse 'ddmmyyyy' e.g. 15062025."""
    s = s.strip()
    if len(s) != 8:
        return None
    try:
        return datetime(int(s[4:8]), int(s[2:4]), int(s[0:2]))
    except ValueError:
        return None


def format_ddmmyyyy(d: datetime) -> str:
    return d.strftime("%d%m%Y")


def format_vector(v) -> str:
    return f"{v[0]:.4f},{v[1]:.4f},{v[2]:.4f}"


def body_position_helio_km(body: str, day: float):
    """Heliocentric position (km) in ecliptic: x,y,z. Circular orbit."""
    a = od.semi_major_axis_km(body)
    T_days = od.orbital_period_days(body)
    theta = 2 * pi * (day / T_days)
    x = a * cos(theta)
    y = a * sin(theta)
    z = 0.0
    return (x, y, z)


def body_velocity_helio_km_s(body: str, day: float):
    """Heliocentric velocity (km/s) in ecliptic. Circular: v = sqrt(GM/a), perpendicular to r."""
    a = od.semi_major_axis_km(body)
    T_days = od.orbital_period_days(body)
    theta = 2 * pi * (day / T_days)
    v = sqrt(GM_SUN / a)
    vx = -v * sin(theta)
    vy = v * cos(theta)
    return (vx, vy, 0.0)


def vec_sub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def vec_add(a, b):
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def vec_mag(v):
    return sqrt(v[0] * v[0] + v[1] * v[1] + v[2] * v[2])


def vec_scale(v, c):
    return (v[0] * c, v[1] * c, v[2] * c)


def hohmann_transfer(a1_km: float, a2_km: float, dep_angle: float, arr_angle: float):
    """
    Hohmann transfer between circular orbits a1 (inner) and a2 (outer).
    a1 < a2: outbound. a1 > a2: inbound.
    Returns (transfer_semi_major_km, time_of_flight_days, v_dep_helio, v_arr_helio)
    where v_dep/arr are velocity vectors of the transfer orbit at dep/arr positions.
    Positions at dep: (a1*cos(dep_angle), a1*sin(dep_angle), 0), same for arr with a2.
    """
    at = (a1_km + a2_km) / 2.0
    # Velocities on transfer orbit at periapsis and apoapsis (vis-viva)
    if a1_km <= a2_km:  # outbound: dep at periapsis, arr at apoapsis
        v_peri = sqrt(GM_SUN * (2.0 / a1_km - 1.0 / at))
        v_apo = sqrt(GM_SUN * (2.0 / a2_km - 1.0 / at))
        # direction at periapsis: along velocity of inner orbit (prograde)
        v_dep = (v_peri * (-sin(dep_angle)), v_peri * cos(dep_angle), 0.0)
        v_arr = (v_apo * (-sin(arr_angle)), v_apo * cos(arr_angle), 0.0)
        tof_sec = pi * sqrt(at ** 3 / GM_SUN)
    else:
        v_apo = sqrt(GM_SUN * (2.0 / a1_km - 1.0 / at))
        v_peri = sqrt(GM_SUN * (2.0 / a2_km - 1.0 / at))
        v_dep = (v_apo * (-sin(dep_angle)), v_apo * cos(dep_angle), 0.0)
        v_arr = (v_peri * (-sin(arr_angle)), v_peri * cos(arr_angle), 0.0)
        tof_sec = pi * sqrt(at ** 3 / GM_SUN)
    tof_days = tof_sec / 86400.0
    return at, tof_days, v_dep, v_arr


def delta_v_departure(body: str, v_planet, v_transfer) -> float:
    """Delta-V (km/s, fuel-equivalent) to go from 12h parking to transfer orbit. Patched conic."""
    v_inf = vec_sub(v_transfer, v_planet)
    v_inf_mag = vec_mag(v_inf)
    mu = od.gm_body_km3s2(body)
    r_park = od.parking_orbit_radius_km(body, 12.0)
    v_park = od.circular_orbital_speed_km_s(mu, r_park)
    # From circular orbit: v_dep^2 = v_esc^2 + v_inf^2 => v_dep = sqrt(2*mu/r + v_inf^2)
    v_esc_sq = 2 * mu / r_park
    v_dep = sqrt(v_esc_sq + v_inf_mag * v_inf_mag)
    return v_dep - v_park


def delta_v_arrival(body: str, v_planet, v_transfer) -> float:
    """Delta-V to capture from transfer to 12h parking."""
    v_inf = vec_sub(v_transfer, v_planet)
    v_inf_mag = vec_mag(v_inf)
    mu = od.gm_body_km3s2(body)
    r_park = od.parking_orbit_radius_km(body, 12.0)
    v_park = od.circular_orbital_speed_km_s(mu, r_park)
    v_dep = sqrt(2 * mu / r_park + v_inf_mag * v_inf_mag)
    return v_dep - v_park


def transfer_direct(origin: str, dest: str, launch_day: float):
    """
    Direct Hohmann-like transfer from origin to dest, launch at launch_day.
    Returns (arrival_day, delta_v_dep, delta_v_arr, launch_vec_helio, arr_vec_helio) or None if invalid.
    """
    if origin == dest:
        return None
    a1 = od.semi_major_axis_km(origin)
    a2 = od.semi_major_axis_km(dest)
    T1 = od.orbital_period_days(origin)
    T2 = od.orbital_period_days(dest)
    dep_angle = 2 * pi * (launch_day / T1)
    # Hohmann TOF
    at = (a1 + a2) / 2.0
    tof_days = pi * sqrt(at ** 3 / GM_SUN) / 86400.0
    arr_day = launch_day + tof_days
    arr_angle = 2 * pi * (arr_day / T2)
    _, _, v_dep_tr, v_arr_tr = hohmann_transfer(a1, a2, dep_angle, arr_angle)
    v_planet_dep = body_velocity_helio_km_s(origin, launch_day)
    v_planet_arr = body_velocity_helio_km_s(dest, arr_day)
    dv_dep = delta_v_departure(origin, v_planet_dep, v_dep_tr)
    dv_arr = delta_v_arrival(dest, v_planet_arr, v_arr_tr)
    if dv_dep < 0 or dv_arr < 0:
        return None
    return {
        "arrival_day": arr_day,
        "delta_v_dep_km_s": dv_dep,
        "delta_v_arr_km_s": dv_arr,
        "launch_vector_helio": v_dep_tr,
        "arrival_vector_helio": v_arr_tr,
        "tof_days": tof_days,
    }


def fuel_for_leg(initial_mass_kg: float, delta_v_km_s: float, Isp_km_s: float) -> float:
    """Fuel consumed (kg) for one burn."""
    return sh.fuel_required_kg(initial_mass_kg, delta_v_km_s, Isp_km_s)


def total_fuel_kg(ship_name: str, payload_kg: float, legs_delta_v: list[float]) -> float | None:
    """Total fuel needed for a sequence of burns (each leg). Returns None if exceeds capacity."""
    spec = sh.get_ship_spec(ship_name)
    if not spec or payload_kg > spec["max_payload_kg"]:
        return None
    dry = spec["dry_mass_kg"]
    cap = spec["fuel_capacity_kg"]
    Isp = spec["Isp_km_s"]
    total = 0.0
    mass = dry + payload_kg + cap  # start full
    for dv in legs_delta_v:
        f = fuel_for_leg(mass, dv, Isp)
        total += f
        mass -= f
        if total > cap or mass < dry + payload_kg:
            return None
    return total if total <= cap else None


def search_launch_window(origin: str, dest: str, ship_name: str, payload_kg: float,
                        start_day: float, end_day: float, step_days: float = 1.0,
                        prefer_fuel_efficient: bool = True):
    """
    Search launch window for best option: either most fuel-efficient or soonest arrival.
    Returns single best option dict or None.
    """
    best = None
    for d in range(int(start_day), int(end_day) + 1, max(1, int(step_days))):
        launch_day = float(d)
        tr = transfer_direct(origin, dest, launch_day)
        if not tr:
            continue
        dv_dep = tr["delta_v_dep_km_s"]
        dv_arr = tr["delta_v_arr_km_s"]
        fuel = total_fuel_kg(ship_name, payload_kg, [dv_dep, dv_arr])
        if fuel is None:
            continue
        cand = {
            "launch_day": launch_day,
            "arrival_day": tr["arrival_day"],
            "delta_v_dep": dv_dep,
            "delta_v_arr": dv_arr,
            "launch_vector": tr["launch_vector_helio"],
            "arrival_vector": tr["arrival_vector_helio"],
            "fuel_kg": fuel,
            "tof_days": tr["tof_days"],
        }
        if best is None:
            best = cand
            continue
        if prefer_fuel_efficient:
            if cand["fuel_kg"] < best["fuel_kg"]:
                best = cand
        else:
            if cand["arrival_day"] < best["arrival_day"]:
                best = cand
    return best


def build_route_option(origin: str, dest: str, ship_name: str, payload_kg: float,
                       start_day: float, end_day: float, prefer_fuel_efficient: bool,
                       with_stops: bool = False):
    """
    Build one route option (efficient or soonest). Optionally try one refuel stop.
    Returns dict suitable for JSON/GUI: launch_date, vectors, deltaV, fuel, stops (if any), arrival.
    """
    step = max(1.0, (end_day - start_day) / 50.0)
    opt = search_launch_window(origin, dest, ship_name, payload_kg,
                               start_day, end_day, step_days=step,
                               prefer_fuel_efficient=prefer_fuel_efficient)
    if opt is None and with_stops:
        # Try with one refuel at an intermediate body (simplified: try midpoint body)
        bodies = od.all_bodies()
        a_orig = od.semi_major_axis_km(origin)
        a_dest = od.semi_major_axis_km(dest)
        for stop in bodies:
            if stop in (origin, dest):
                continue
            a_mid = od.semi_major_axis_km(stop)
            if not (min(a_orig, a_dest) <= a_mid <= max(a_orig, a_dest)):
                continue
            # Two legs: origin -> stop -> dest
            opt1 = search_launch_window(origin, stop, ship_name, payload_kg, start_day, end_day, step, prefer_fuel_efficient)
            if opt1 is None:
                continue
            arr1 = opt1["arrival_day"]
            # Refuel: 1 s per kg; max 3 days at dock. So relaunch by arr1 + 3.
            relaunch_start = arr1
            relaunch_end = min(end_day, arr1 + 3.0)
            opt2 = search_launch_window(stop, dest, ship_name, payload_kg, relaunch_start, relaunch_end, step / 2.0, prefer_fuel_efficient)
            if opt2 is None:
                continue
            fuel1 = total_fuel_kg(ship_name, payload_kg, [opt1["delta_v_dep"], opt1["delta_v_arr"]])
            fuel2 = total_fuel_kg(ship_name, payload_kg, [opt2["delta_v_dep"], opt2["delta_v_arr"]])
            if fuel1 is None or fuel2 is None:
                continue
            refuel_amt = fuel1  # amount used on leg 1, so we refuel that much at stop
            total_f = fuel1 + fuel2
            spec = sh.get_ship_spec(ship_name)
            if spec and total_f <= spec["fuel_capacity_kg"]:
                opt = {
                    "launch_day": opt1["launch_day"],
                    "arrival_day": opt2["arrival_day"],
                    "delta_v_dep": opt1["delta_v_dep"],
                    "delta_v_arr": opt2["delta_v_arr"],
                    "launch_vector": opt1["launch_vector"],
                    "arrival_vector": opt2["arrival_vector"],
                    "fuel_kg": total_f,
                    "tof_days": opt1["tof_days"] + opt2["tof_days"],
                    "stop": {
                        "body": stop,
                        "arrival_day": opt1["arrival_day"],
                        "arrival_vector": opt1["arrival_vector"],
                        "delta_v_arr": opt1["delta_v_arr"],
                        "refuel_kg": refuel_amt,
                        "relaunch_day": opt2["launch_day"],
                        "relaunch_vector": opt2["launch_vector"],
                        "relaunch_delta_v": opt2["delta_v_dep"],
                    },
                }
                break
    if opt is None:
        return None
    # Format for output
    launch_date = days_to_date(opt["launch_day"])
    arrival_date = days_to_date(opt["arrival_day"])
    out = {
        "Launch date": format_ddmmyyyy(launch_date),
        "Launch vector": format_vector(opt["launch_vector"]),
        "Launch deltaV": round(opt["delta_v_dep"], 4),
        "Fuel": round(opt["fuel_kg"], 2),
        "Arrival date": format_ddmmyyyy(arrival_date),
        "Arrival vector": format_vector(opt["arrival_vector"]),
        "Arrival deltaV": round(opt["delta_v_arr"], 4),
    }
    if "stop" in opt:
        s = opt["stop"]
        out["Stop 1"] = {
            "Arrival date": format_ddmmyyyy(days_to_date(s["arrival_day"])),
            "Arrival vector": format_vector(s["arrival_vector"]),
            "Arrival deltaV": round(s["delta_v_arr"], 4),
            "Refuel amount": round(s["refuel_kg"], 2),
            "Relaunch date": format_ddmmyyyy(days_to_date(s["relaunch_day"])),
            "Relaunch vector": format_vector(s["relaunch_vector"]),
            "Relaunch deltaV": round(s["relaunch_delta_v"], 4),
        }
        out["_waypoints"] = [
            (opt["launch_day"], origin),
            (s["arrival_day"], s["body"]),
            (opt["arrival_day"], dest),
        ]
    else:
        out["_waypoints"] = [(opt["launch_day"], origin), (opt["arrival_day"], dest)]
    return out


def compute_both_options(origin: str, dest: str, ship_name: str, payload_kg: float,
                        window_start: str, window_end: str):
    """
    Compute both 'Efficient flight parameters' and 'Soonest arrival flight parameters'.
    window_start, window_end: ddmmyyyy.
    Returns dict with "Flight impossible", "Efficient flight parameters", "Soonest arrival flight parameters".
    """
    start_d = parse_ddmmyyyy(window_start)
    end_d = parse_ddmmyyyy(window_end)
    if start_d is None or end_d is None or start_d > end_d:
        return {"Flight impossible": True, "error": "Invalid launch window dates"}
    if origin not in od.BODIES or dest not in od.BODIES:
        return {"Flight impossible": True, "error": "Unknown origin or destination"}
    if not sh.get_ship_spec(ship_name):
        return {"Flight impossible": True, "error": "Unknown ship"}
    if not sh.can_carry_payload(ship_name, payload_kg):
        return {"Flight impossible": True, "error": "Payload exceeds ship max payload"}
    start_day = date_to_days(start_d)
    end_day = date_to_days(end_d)
    efficient = build_route_option(origin, dest, ship_name, payload_kg, start_day, end_day, prefer_fuel_efficient=True, with_stops=True)
    soonest = build_route_option(origin, dest, ship_name, payload_kg, start_day, end_day, prefer_fuel_efficient=False, with_stops=True)
    if efficient is None and soonest is None:
        return {"Flight impossible": True, "error": "No valid trajectory in launch window"}
    return {
        "Flight impossible": False,
        "Efficient flight parameters": efficient or {},
        "Soonest arrival flight parameters": soonest or {},
    }
