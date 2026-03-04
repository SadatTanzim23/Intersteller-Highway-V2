"OEC PROJECT"
"THE GOLDEN AGE OF SPACE COMMERCE"
"By: SADAT TANZIM, ZAIN USMANI, AFFAN SYED, ABDERRAHMENE NACERI"

import sys
import random
import threading
if len(sys.argv) == 7:
    import cli
    sys.exit(cli.main(sys.argv[1:]))

from pygame import *
from math import *

init()
font.init()

WIDTH, HEIGHT = 1100, 700
screen = display.set_mode((WIDTH, HEIGHT), DOUBLEBUF)
display.set_caption("INTERSTELLER HIGHWAY")

# Design system: dark theme, professional
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BG_DARK = (18, 20, 28)
BG_PANEL = (28, 32, 44)
BG_CARD = (38, 42, 58)
ACCENT = (70, 130, 255)
ACCENT_HOVER = (100, 160, 255)
ACCENT_DIM = (50, 90, 180)
SUCCESS = (80, 200, 140)
WARNING = (255, 190, 80)
ERROR_RED = (220, 80, 80)
TEXT_PRIMARY = (240, 242, 248)
TEXT_SECONDARY = (160, 168, 192)
BORDER = (60, 68, 90)
BORDER_FOCUS = (100, 140, 220)
RADIUS = 10
RADIUS_BTN = 12

# Legacy aliases for compatibility
BLUE = ACCENT
GREEN = SUCCESS
GRAY = TEXT_SECONDARY
YELLOW = WARNING
RED = ERROR_RED

# Fonts – prefer Audiowide .ttf in project folder, with fallbacks
try:
    # If Audiowide.ttf is in this folder, use it directly (slightly smaller sizes for this face)
    MAIN_TTF = "Audiowide.ttf"
    title_font = font.Font(MAIN_TTF, 26)
    main_font = font.Font(MAIN_TTF, 20)
    ui_font = font.Font(MAIN_TTF, 18)
    small_font = font.Font(MAIN_TTF, 14)
except Exception:
    # Fallback to system font names
    try:
        title_font = font.SysFont("Audiowide", 26, bold=False)
        main_font = font.SysFont("Audiowide", 20, bold=False)
        ui_font = font.SysFont("Audiowide", 18, bold=False)
        small_font = font.SysFont("Audiowide", 14, bold=False)
    except Exception:
        try:
            title_font = font.SysFont("Arial", 26, bold=False)
            main_font = font.SysFont("Arial", 20, bold=False)
            ui_font = font.SysFont("Arial", 18, bold=False)
            small_font = font.SysFont("Arial", 14, bold=False)
        except Exception:
            title_font = font.SysFont(None, 30)
            main_font = font.SysFont(None, 24)
            ui_font = font.SysFont(None, 22)
            small_font = font.SysFont(None, 18)
coord_font = small_font
# Small font for "R" inside the rocket marker dot during route animation
try:
    rocket_marker_font = font.Font(MAIN_TTF, 10)
except Exception:
    try:
        rocket_marker_font = font.SysFont("Audiowide", 12, bold=True)
    except Exception:
        try:
            rocket_marker_font = font.SysFont("Arial", 12, bold=True)
        except Exception:
            rocket_marker_font = font.SysFont(None, 12)

clock = time.Clock()
FPS = 60
current_screen = "menu"

# Menu buttons (centered vertically with title panel)
btn_mission = Rect(90, 515, 200, 52)
btn_instructions = Rect(330, 515, 200, 52)
btn_rockets = Rect(570, 515, 200, 52)
btn_past_routes = Rect(810, 515, 200, 52)
btn_launch = Rect(450, 420, 200, 52)
btn_back = Rect(20, 16, 100, 40)
btn_exit = Rect(WIDTH - 120, 16, 100, 40)
# Global music toggle button (bottom-right, all screens)
btn_music = Rect(WIDTH - 190, HEIGHT - 42, 170, 32)

#background images
menu_bg = image.load("images/ss.jpg").convert()
screen1_bg = image.load("images/bg.jpg").convert()
screen2_bg = image.load("images/bbg.jpg").convert()
menu_bg = transform.scale(menu_bg, (WIDTH, HEIGHT))
screen1_bg = transform.scale(screen1_bg, (WIDTH, HEIGHT))
screen2_bg = transform.scale(screen2_bg, (WIDTH, HEIGHT))

# Pre-made translucent overlays to avoid recreating large surfaces every frame
overlay_menu = Surface((WIDTH, HEIGHT), SRCALPHA)
overlay_menu.fill((0, 0, 0, 140))
overlay_calc = Surface((WIDTH, HEIGHT), SRCALPHA)
overlay_calc.fill((0, 0, 0, 180))

# Background music (space.mp3) – looped
music_playing = False
music_available = False
try:
    mixer.music.load("images/space.mp3")
    mixer.music.set_volume(0.4)
    mixer.music.play(-1)
    music_playing = True
    music_available = True
except Exception:
    music_playing = False
    music_available = False

# Logo (cache scaled version to avoid per-frame scaling)
logo_img = None
logo_scaled_cache = None
try:
    logo_img = image.load("images/lgo.png").convert_alpha()
    if logo_img:
        # Scale to fit nicely inside the title panel: taller and a bit wider
        target_h = 96
        max_w = 720
        scale = target_h / logo_img.get_height()
        w = int(logo_img.get_width() * scale)
        h = target_h
        if w > max_w:
            scale = max_w / logo_img.get_width()
            w = max_w
            h = int(logo_img.get_height() * scale)
        logo_scaled_cache = transform.smoothscale(logo_img, (w, h))
except Exception:
    logo_img = None

#planets for the dropdowns (all eight planets, Pluto, Ceres - refuel stations)
planet_options = [
    "Mercury", "Venus", "Earth", "Mars",
    "Jupiter", "Saturn", "Uranus", "Neptune",
    "Pluto", "Ceres"
]

# Load planet images (from images/ or images/planets/)
planet_imgs = {}
planet_imgs_sim = {}   # scaled for animation window (cached)
planet_imgs_strip = {} # scaled for route summary strip (cached)
SIM_PLANET_SIZE = 28
for p in planet_options:
    planet_imgs[p] = None
    for path in (f"images/{p.lower()}.png", f"images/planets/{p.lower()}.png"):
        try:
            planet_imgs[p] = image.load(path).convert_alpha()
            break
        except Exception:
            continue
    if planet_imgs[p] is not None:
        planet_imgs_sim[p] = transform.smoothscale(planet_imgs[p], (SIM_PLANET_SIZE, SIM_PLANET_SIZE))
        planet_imgs_strip[p] = transform.smoothscale(planet_imgs[p], (56, 56))
    else:
        planet_imgs_sim[p] = None
        planet_imgs_strip[p] = None

# Departure and destination dropdown box (same width as ship for alignment)
dep_rect = Rect(270, 100, 400, 40)
dest_rect = Rect(270, 160, 400, 40)
dep_open = False
dest_open = False
dep_selected = "Earth"
dest_selected = "Mars"

input_rects = [
    Rect(270, 220, 400, 40),  # launch window
    Rect(270, 340, 400, 40),  # payload
]
input_labels = ["Launch window", "Payload mass (kg)"]
input_placeholders = ["e.g. 01012025 31012025", "e.g. 500"]
input_texts = ["", ""]
active_input = -1

# Ship dropdown (ICTB-certified ships); display strings include max payload
ship_rect = Rect(270, 280, 400, 40)
ship_open = False
ship_options = [
    "Chevrolet Super Sonic", "The Planet Hopper", "Moonivan",
    "Blue Origin Delivery Ship", "Yamaha Space Cycle",
    "Ford F-1500", "Behemoth"
]
ship_selected = ship_options[0]

def _ship_display_name(name):
    """Return 'Ship name (max X kg)' for display."""
    try:
        import ships as _sh
        spec = _sh.get_ship_spec(name)
        if spec:
            return f"{name} (max {int(spec['max_payload_kg'])} kg)"
    except Exception:
        pass
    return name

ship_display_options = [_ship_display_name(s) for s in ship_options]
HEADER_H = 72  # single-row header height for plan/instructions/simulation/past routes

# Rocket images for plan-trade-route panel (one per ship, same order as ship_options)
ROCKET_PANEL_W = 140  # display width for rocket image
rocket_imgs = []
for i in range(len(ship_options)):
    path = f"images/rockets/rocket{i + 1}.png"
    try:
        img = image.load(path).convert_alpha()
        h = int(img.get_height() * (ROCKET_PANEL_W / img.get_width()))
        rocket_imgs.append(transform.smoothscale(img, (ROCKET_PANEL_W, min(h, 360))))
    except Exception:
        rocket_imgs.append(None)

# Cached vertically rotated ship names (so we don't rotate every frame)
_rotated_ship_names = {}
for name in ship_options:
    lbl = small_font.render(name, True, TEXT_PRIMARY)
    _rotated_ship_names[name] = transform.rotate(lbl, 90)

#simulation data for the mission trade
orbit_data = {
    "Mercury": (60,  1.30),
    "Venus":   (90,  1.10),
    "Earth":   (120, 1.00),
    "Mars":    (150, 0.90),
    "Jupiter": (190, 0.70),
    "Saturn":  (230, 0.60),
    "Uranus":  (270, 0.50),
    "Neptune": (310, 0.45),
    "Pluto":   (350, 0.35),
    "Ceres":   (250, 0.65),
}

sun_pos = (WIDTH // 2, HEIGHT // 2 + 40)

# Sun image (optional). If not found, we fall back to a yellow circle.
sun_img = None
sun_img_rect = None
try:
    raw_sun = image.load("images/sun.png").convert_alpha()
    # Scale sun to look similar to the old circle (a bit larger for detail)
    target_r = 26
    diameter = target_r * 2
    sun_img = transform.smoothscale(raw_sun, (diameter, diameter))
    sun_img_rect = sun_img.get_rect(center=sun_pos)
except Exception:
    sun_img = None
    sun_img_rect = None
sim_time = 0.0

#ship travel state (set when LAUNCH is clicked)
travel_active = False
travel_t = 0.0
travel_from = "Earth"
travel_to = "Mars"
travel_payload = 0.0
travel_ship_name = ""
travel_window = ""

# route computation result (set when LAUNCH runs trajectory engine)
route_result = None
route_error = ""
route_view = 0  # 0 = Efficient, 1 = Soonest
DAY_TO_SIM = 2 * pi / 365.25
# Route options (screen4) header: taller panel, title centered, buttons with breathing room
HEADER_H_ROUTE = 118
_route_title_y = 28
_route_subtitle_y = 50
_route_btn_y = 76
_btn_w1, _btn_w2, _btn_w3 = 200, 200, 190
_btn_gap = 14
_btn_row_width = _btn_w1 + _btn_gap + _btn_w2 + _btn_gap + _btn_w3
_btn_row_x = (WIDTH - _btn_row_width) // 2
btn_efficient = Rect(_btn_row_x, _route_btn_y, _btn_w1, 36)
btn_soonest = Rect(_btn_row_x + _btn_w1 + _btn_gap, _route_btn_y, _btn_w2, 36)
btn_animate = Rect(_btn_row_x + _btn_w1 + _btn_gap + _btn_w2 + _btn_gap, _route_btn_y, _btn_w3, 36)
ROUTE_CONTENT_TOP = HEADER_H_ROUTE + 16
past_routes_list = []
past_route_selected = -1

# route animation state (for live orbit animation)
route_animating = False
route_anim_option = 0  # 0 = efficient, 1 = soonest
route_anim_time_day = 0.0
route_anim_total_days = 0.0
route_anim_segments = []  # list of (start_day, end_day, from_body, to_body)

# Non-blocking route calculation (run in thread so UI stays responsive)
_calc_done = None  # (result, from, to, ship, payload, w_start, w_end) when set by worker
_calc_in_progress = False


def _run_route_calculation(origin, dest, ship_name, payload_kg, w_start, w_end):
    global _calc_done, _calc_in_progress
    try:
        import trajectory as tr
        result = tr.compute_both_options(origin, dest, ship_name, payload_kg, w_start, w_end)
        _calc_done = (result, origin, dest, ship_name, payload_kg, w_start, w_end)
    except Exception as e:
        _calc_done = ({"Flight impossible": True, "error": str(e)}, origin, dest, ship_name, payload_kg, w_start, w_end)
    _calc_in_progress = False

# simple starfield background (cached surfs for performance)
STAR_COUNT = 80
stars = []
_star_surfs = {}  # cached surfaces per (r, alpha)


def init_starfield():
    global stars, _star_surfs
    stars = []
    _star_surfs.clear()
    for _ in range(STAR_COUNT):
        layer = random.choice([1, 1, 1, 2, 2, 3])
        speed = {1: 6.0, 2: 12.0, 3: 20.0}[layer]
        radius = {1: 1, 2: 2, 3: 3}[layer]
        alpha = {1: 100, 2: 160, 3: 200}[layer]
        stars.append({
            "x": random.uniform(0, WIDTH),
            "y": random.uniform(0, HEIGHT),
            "speed": speed,
            "r": radius,
            "a": alpha,
        })
    # Pre-create one surface per (r, alpha) so we don't allocate every frame
    for r in (1, 2, 3):
        for a in (100, 160, 200):
            key = (r, a)
            surf = Surface((r * 2 + 1, r * 2 + 1), SRCALPHA)
            draw.circle(surf, (255, 255, 255, a), (r, r), r)
            _star_surfs[key] = surf


def update_starfield(dt):
    for s in stars:
        s["y"] += s["speed"] * dt
        if s["y"] > HEIGHT + 5:
            s["y"] = -5
            s["x"] = random.uniform(0, WIDTH)


def draw_starfield():
    for s in stars:
        r, a = s["r"], s["a"]
        surf = _star_surfs.get((r, a))
        if surf:
            screen.blit(surf, (int(s["x"]) - r, int(s["y"]) - r))
        else:
            draw.circle(screen, (255, 255, 255), (int(s["x"]), int(s["y"])), r)


init_starfield()

# Clear previous saved routes so the app starts with a clean history
try:
    import route_storage as _rs
    _rs.clear_all_routes()
except Exception:
    pass


def blit_text_clipped(text, font_obj, color, pos, max_width):
    """Render text and truncate with ellipsis so it fits max_width."""
    surf = font_obj.render(text, True, color)
    if surf.get_width() <= max_width:
        screen.blit(surf, pos)
        return
    ellipsis = "…"
    txt = text
    # Leave at least a few characters when clipping
    while len(txt) > 3:
        txt = txt[:-1]
        candidate = font_obj.render(txt + ellipsis, True, color)
        if candidate.get_width() <= max_width:
            screen.blit(candidate, pos)
            return
    # Fallback: just draw ellipsis
    ell = font_obj.render(ellipsis, True, color)
    screen.blit(ell, pos)

def safe_float(s, default=0.0):
    try:
        return float(s.strip())
    except Exception:
        return default


def draw_panel(rect, alpha=255, border=True):
    """Draw a rounded panel (no per-frame Surface when opaque for speed)."""
    if alpha >= 250:
        draw.rect(screen, BG_PANEL, rect, border_radius=RADIUS)
    else:
        surf = Surface((rect.w, rect.h), SRCALPHA)
        surf.fill((*BG_PANEL[:3], alpha))
        screen.blit(surf, (rect.x, rect.y))
    if border:
        draw.rect(screen, BORDER, rect, 1, border_radius=RADIUS)


def draw_button(rect, text, base_col, hover_col, text_col=BLACK, border_col=None):
    mx, my = mouse.get_pos()
    hovering = rect.collidepoint((mx, my))
    col = hover_col if hovering else base_col
    border_col = border_col or BORDER

    # Subtle shadow
    shadow_rect = rect.copy()
    shadow_rect.x += 3
    shadow_rect.y += 3
    draw.rect(screen, (0, 0, 0, 80), shadow_rect, border_radius=RADIUS_BTN)

    draw.rect(screen, col, rect, border_radius=RADIUS_BTN)
    draw.rect(screen, border_col, rect, 2, border_radius=RADIUS_BTN)

    # Pick a font that fits inside the button
    chosen_label = None
    for f in (main_font, ui_font, small_font):
        label = f.render(text, True, text_col)
        if label.get_width() <= rect.w - 16 and label.get_height() <= rect.h - 8:
            chosen_label = label
            break
    if chosen_label is None:
        chosen_label = small_font.render(text, True, text_col)
    screen.blit(chosen_label, chosen_label.get_rect(center=rect.center))
    return hovering


def draw_input_box(r, text, is_active, placeholder=""):
    fill = BG_CARD
    border_col = BORDER_FOCUS if is_active else BORDER
    draw.rect(screen, fill, r, border_radius=RADIUS)
    draw.rect(screen, border_col, r, 2 if is_active else 1, border_radius=RADIUS)
    display_text = text if text else placeholder
    text_col = TEXT_PRIMARY if text else TEXT_SECONDARY
    t = ui_font.render(display_text, True, text_col)
    # Clip if too long
    if t.get_width() > r.w - 24:
        screen.blit(t, (r.x + 12, r.y + (r.h - t.get_height()) // 2), (t.get_width() - (r.w - 28), 0, r.w - 28, t.get_height()))
    else:
        screen.blit(t, (r.x + 12, r.y + (r.h - t.get_height()) // 2))


def draw_dropdown_box(rect, selected, open_state, options, draw_list=True):
    mx, my = mouse.get_pos()
    hover = rect.collidepoint((mx, my))
    fill = (BG_CARD[0] + 15, BG_CARD[1] + 15, BG_CARD[2] + 15) if hover and not open_state else BG_CARD
    border_col = BORDER_FOCUS if open_state else BORDER
    draw.rect(screen, fill, rect, border_radius=RADIUS)
    draw.rect(screen, border_col, rect, 2 if open_state else 1, border_radius=RADIUS)
    sel_y = rect.y + (rect.h - ui_font.get_height()) // 2
    blit_text_clipped(selected, ui_font, TEXT_PRIMARY, (rect.x + 12, sel_y), rect.w - 44)

    # Arrow (rotates when open)
    arrow_y = rect.y + rect.h // 2
    arrow_x = rect.right - 28
    if open_state:
        draw.polygon(screen, TEXT_SECONDARY, [(arrow_x, arrow_y - 5), (arrow_x + 8, arrow_y - 5), (arrow_x + 4, arrow_y + 4)])
    else:
        draw.polygon(screen, TEXT_SECONDARY, [(arrow_x, arrow_y + 5), (arrow_x + 8, arrow_y + 5), (arrow_x + 4, arrow_y - 4)])

    if open_state and draw_list:
        for i, opt in enumerate(options):
            opt_rect = Rect(rect.x, rect.y + (i + 1) * rect.h, rect.w, rect.h)
            opt_hover = opt_rect.collidepoint((mx, my))
            opt_fill = (BG_CARD[0] + 20, BG_CARD[1] + 20, BG_CARD[2] + 20) if opt_hover else BG_CARD
            draw.rect(screen, opt_fill, opt_rect)
            if i < len(options) - 1:
                draw.line(screen, BORDER, (opt_rect.x, opt_rect.bottom), (opt_rect.right, opt_rect.bottom), 1)
            opt_y = opt_rect.y + (opt_rect.h - ui_font.get_height()) // 2
            blit_text_clipped(opt, ui_font, TEXT_PRIMARY, (opt_rect.x + 12, opt_y), opt_rect.w - 24)


def pick_dropdown_option(pos, rect, open_state, options):
    if not open_state:
        return None
    for i, opt in enumerate(options):
        opt_rect = Rect(rect.x, rect.y + (i + 1) * rect.h, rect.w, rect.h)
        if opt_rect.collidepoint(pos):
            return opt
    return None


def planet_xy(name, t):
    #MATH LOGIC ssm
    r, spd = orbit_data.get(name, (120, 1.0))#ach planet has an orbit radius "r" and an orbit speed "spd"
    ang = t * spd#we convert time into an angle
    #then we use trig to place the planet on a circle:
    #x = center_x + cos(angle) * r
    #y = center_y + sin(angle) * r
    x = sun_pos[0] + cos(ang) * r
    y = sun_pos[1] + sin(ang) * r * 0.7#we multiply y by 0.7 to squash the circle into an ellipse which gives us a 3dish look
    return (int(x), int(y))

def draw_orbit(r):
    rect_orb = Rect(0, 0, r * 2, int(r * 2 * 0.7))
    rect_orb.center = sun_pos
    draw.ellipse(screen, BORDER, rect_orb, 1)

# main loop
running = True
while running:
    dt = clock.tick(FPS) / 1000.0
    sim_time += dt * 1.2
    mx, my = mouse.get_pos()

    # Apply finished route calculation (from background thread)
    if _calc_done is not None:
        result, origin, dest, ship_name, payload_kg, w_start, w_end = _calc_done
        globals()["_calc_done"] = None
        globals()["route_result"] = result
        globals()["travel_from"] = origin
        globals()["travel_to"] = dest
        globals()["travel_ship_name"] = ship_name
        globals()["travel_payload"] = payload_kg
        if result.get("Flight impossible"):
            globals()["route_error"] = result.get("error", "No valid trajectory")
            current_screen = "screen1"
        else:
            try:
                import route_storage as rs
                rs.save_route(origin, dest, ship_name, payload_kg, w_start, w_end, result)
            except Exception:
                pass
            globals()["route_error"] = ""
            globals()["travel_active"] = True
            globals()["travel_t"] = 0.0
            globals()["route_view"] = 0
            current_screen = "screen4"
        dep_open = dest_open = ship_open = False
        active_input = -1

    # background starfield animation
    update_starfield(dt)

    # advance route animation time (in days) if active
    if route_animating and route_anim_segments:
        anim_duration_sec = 25.0  # whole route shown in ~25 seconds
        speed_days_per_sec = route_anim_total_days / anim_duration_sec
        route_anim_time_day += dt * speed_days_per_sec
        last_end = route_anim_segments[-1][1]
        if route_anim_time_day >= last_end:
            route_anim_time_day = last_end
            route_animating = False

    for evt in event.get():
        if evt.type == QUIT:
            running = False

        if evt.type == MOUSEBUTTONDOWN:
            # Only react to left click so one click = one action (smoother, no accidental right-click)
            if evt.button != 1:
                continue
            if btn_exit.collidepoint(evt.pos):#exit button use
                running = False
                continue

            if btn_back.collidepoint(evt.pos):#back button use
                if current_screen in ["screen1", "screen2", "screen3", "screen4", "screen5", "screen6"]:
                    current_screen = "menu"
                    dep_open = dest_open = ship_open = False
                    active_input = -1
                    route_animating = False
                    route_anim_segments = []
                continue

            # Global music toggle button (all screens)
            if btn_music.collidepoint(evt.pos) and music_available:
                if music_playing:
                    try:
                        mixer.music.pause()
                    except Exception:
                        pass
                    music_playing = False
                else:
                    try:
                        mixer.music.unpause()
                    except Exception:
                        try:
                            mixer.music.play(-1)
                        except Exception:
                            pass
                    music_playing = True
                continue

            if current_screen == "menu":
                if btn_mission.collidepoint(evt.pos):
                    globals()["route_error"] = ""
                    current_screen = "screen1"
                elif btn_instructions.collidepoint(evt.pos):
                    current_screen = "screen2"
                elif btn_rockets.collidepoint(evt.pos):
                    current_screen = "screen6"
                elif btn_past_routes.collidepoint(evt.pos):
                    try:
                        import route_storage as rs
                        globals()["past_routes_list"] = list(reversed(rs.get_all_routes()))
                    except Exception:
                        globals()["past_routes_list"] = []
                    current_screen = "screen5"

            elif current_screen == "screen1":
                clicked_any_dropdown = False

                if btn_launch.collidepoint(evt.pos) and not _calc_in_progress:
                    travel_from = dep_selected
                    travel_to = dest_selected
                    travel_window = input_texts[0].strip()
                    travel_payload = safe_float(input_texts[1], 0.0)
                    travel_ship_name = ship_selected
                    win_text = travel_window.replace("-", " ").split()
                    if len(win_text) >= 2:
                        w_start, w_end = win_text[0], win_text[1]
                    elif len(win_text) == 1:
                        w_start = w_end = win_text[0]
                    else:
                        w_start = w_end = "01012025"
                    globals()["_calc_in_progress"] = True
                    t = threading.Thread(
                        target=_run_route_calculation,
                        args=(travel_from, travel_to, travel_ship_name, travel_payload, w_start, w_end),
                        daemon=True,
                    )
                    t.start()
                    dep_open = dest_open = ship_open = False
                    active_input = -1
                    continue

                #if drop down is open select first to make it wasier
                picked = pick_dropdown_option(evt.pos, dep_rect, dep_open, planet_options)
                if picked:
                    dep_selected = picked
                    dep_open = False
                    clicked_any_dropdown = True

                picked = pick_dropdown_option(evt.pos, dest_rect, dest_open, planet_options)
                if picked:
                    dest_selected = picked
                    dest_open = False
                    clicked_any_dropdown = True

                picked = pick_dropdown_option(evt.pos, ship_rect, ship_open, ship_display_options)
                if picked:
                    for i, d in enumerate(ship_display_options):
                        if d == picked:
                            globals()["ship_selected"] = ship_options[i]
                            break
                    ship_open = False
                    clicked_any_dropdown = True

                # if we selected something, STOP (do not toggle other dropdowns)
                if clicked_any_dropdown:
                    continue

                #departure dropdown
                if dep_rect.collidepoint(evt.pos):
                    dep_open = not dep_open
                    dest_open = False
                    ship_open = False
                    clicked_any_dropdown = True

                #destination dropdown
                elif dest_rect.collidepoint(evt.pos):
                    dest_open = not dest_open
                    dep_open = False
                    ship_open = False
                    clicked_any_dropdown = True

                #ship dropdown
                elif ship_rect.collidepoint(evt.pos):
                    ship_open = not ship_open
                    dep_open = False
                    dest_open = False
                    clicked_any_dropdown = True


                # input boxes
                active_input = -1
                if not clicked_any_dropdown:
                    for i, r in enumerate(input_rects):
                        if r.collidepoint(evt.pos):
                            active_input = i
                            break

                #click elsewhere closes dropdowns
                if not clicked_any_dropdown and active_input == -1:
                    dep_open = dest_open = ship_open = False

            elif current_screen == "screen4":
                if btn_efficient.collidepoint(evt.pos):
                    globals()["route_view"] = 0
                elif btn_soonest.collidepoint(evt.pos):
                    globals()["route_view"] = 1
                elif btn_animate.collidepoint(evt.pos) and route_result and not route_result.get("Flight impossible"):
                    opt_key = "Efficient flight parameters" if route_view == 0 else "Soonest arrival flight parameters"
                    opt = route_result.get(opt_key) or {}
                    waypoints = opt.get("_waypoints", [])
                    if waypoints and len(waypoints) >= 2:
                        segs = []
                        start_day = waypoints[0][0]
                        end_day = waypoints[-1][0]
                        total_days = max(1e-6, end_day - start_day)
                        for i in range(len(waypoints) - 1):
                            d0, b0 = waypoints[i]
                            d1, b1 = waypoints[i + 1]
                            if d1 <= d0:
                                continue
                            segs.append((d0, d1, b0, b1))
                        if segs:
                            globals()["route_animating"] = True
                            globals()["route_anim_option"] = route_view
                            globals()["route_anim_segments"] = segs
                            globals()["route_anim_total_days"] = total_days
                            globals()["route_anim_time_day"] = start_day
                            # reset simple travel animation
                            globals()["travel_active"] = True
                            globals()["travel_t"] = 0.0
                            current_screen = "screen3"

            elif current_screen == "screen5":
                for i, r in enumerate(past_routes_list):
                    rect = Rect(80, HEADER_H + 20 + i * 48, WIDTH - 160, 44)
                    if rect.collidepoint(evt.pos):
                        globals()["past_route_selected"] = i
                        globals()["route_result"] = r.get("result")
                        globals()["travel_from"] = r.get("origin", "")
                        globals()["travel_to"] = r.get("destination", "")
                        current_screen = "screen4"
                        break

        if evt.type == KEYDOWN and current_screen == "screen1":
            if active_input != -1:
                if evt.key == K_BACKSPACE:
                    input_texts[active_input] = input_texts[active_input][:-1]
                else:
                    max_len = 24 if active_input == 0 else 12
                    if len(input_texts[active_input]) < max_len:
                        input_texts[active_input] += evt.unicode

    # Per-frame music toggle button style
    music_label = "Music: On" if music_playing and music_available else "Music: Off"
    music_fill = ACCENT if music_playing and music_available else BG_CARD
    music_hover_fill = ACCENT_HOVER if music_playing and music_available else (60, 64, 80)
    music_text_col = WHITE if music_playing and music_available else TEXT_PRIMARY
    music_border = ACCENT_DIM if music_playing and music_available else BORDER

    #draw
    if current_screen == "menu":
        screen.fill(BG_DARK)
        if menu_bg:
            screen.blit(menu_bg, (0, 0))
        screen.blit(overlay_menu, (0, 0))
        draw_starfield()

        # Logo and title block (lower, centered with buttons; more transparent)
        title_block = Rect(50, 145, WIDTH - 100, 320)
        draw_panel(title_block, alpha=140)
        block_center_x = title_block.centerx
        if logo_scaled_cache:
            logo_rect = logo_scaled_cache.get_rect(center=(block_center_x, title_block.y + 100))
            screen.blit(logo_scaled_cache, logo_rect)
        tagline1 = ui_font.render("Interplanetary trade route planner", True, TEXT_SECONDARY)
        tagline2 = small_font.render("Plan missions • Compare routes • Optimize fuel & time", True, TEXT_SECONDARY)
        screen.blit(tagline1, tagline1.get_rect(center=(block_center_x, title_block.y + 175)))
        screen.blit(tagline2, tagline2.get_rect(center=(block_center_x, title_block.y + 210)))

        # Menu buttons
        draw_button(btn_mission, "New route", ACCENT, ACCENT_HOVER, text_col=WHITE, border_col=ACCENT_DIM)
        draw_button(btn_instructions, "Instructions", BG_PANEL, BG_CARD, text_col=TEXT_PRIMARY, border_col=BORDER)
        draw_button(btn_rockets, "Rocket specs", BG_PANEL, BG_CARD, text_col=TEXT_PRIMARY, border_col=BORDER)
        draw_button(btn_past_routes, "Past routes", BG_PANEL, BG_CARD, text_col=TEXT_PRIMARY, border_col=BORDER)
        draw_button(btn_exit, "Exit", ERROR_RED, (200, 90, 90), text_col=WHITE, border_col=(180, 60, 60))
        # footer + music toggle
        screen.blit(small_font.render("OEC Project", True, TEXT_SECONDARY), (12, HEIGHT - 24))
        draw_button(btn_music, music_label, music_fill, music_hover_fill, text_col=music_text_col, border_col=music_border)

    elif current_screen == "screen1":
        screen.fill(BG_DARK)
        draw_starfield()
        # Header bar (taller for better UI)
        header_rect = Rect(0, 0, WIDTH, HEADER_H)
        draw.rect(screen, BG_PANEL, header_rect)
        draw.line(screen, BORDER, (0, HEADER_H), (WIDTH, HEADER_H), 1)
        draw_button(btn_back, "← Back", BG_PANEL, BG_CARD, text_col=TEXT_PRIMARY, border_col=BORDER)
        draw_button(btn_exit, "Exit", ERROR_RED, (200, 90, 90), text_col=WHITE, border_col=(180, 60, 60))
        t1 = title_font.render("Plan Trade Route", True, TEXT_PRIMARY)
        screen.blit(t1, t1.get_rect(center=(WIDTH // 2, HEADER_H // 2 - 10)))
        t2 = small_font.render("Departure, destination, ship, and launch window", True, TEXT_SECONDARY)
        screen.blit(t2, t2.get_rect(center=(WIDTH // 2, HEADER_H // 2 + 14)))

        # Form card (left) and rocket panel (right)
        form_card = Rect(40, HEADER_H + 16, 680, 400)
        rocket_panel = Rect(740, HEADER_H + 16, 320, 400)
        draw_panel(form_card, alpha=220)
        draw_panel(rocket_panel, alpha=220)
        # Vertical ship name on the left; rocket image centered in the rest of the panel (middle-right)
        name_strip_w = 36
        try:
            ship_idx = ship_options.index(ship_selected)
            # Ship name drawn vertically (cached, no per-frame rotate)
            rotated = _rotated_ship_names.get(ship_selected)
            if rotated is not None:
                rw, rh = rotated.get_size()
                screen.blit(rotated, (rocket_panel.x + (name_strip_w - rw) // 2, rocket_panel.centery - rh // 2))
            # Rocket image centered in the panel (middle-right), so not pushed to the edge
            if ship_idx < len(rocket_imgs) and rocket_imgs[ship_idx] is not None:
                rimg = rocket_imgs[ship_idx]
                img_area = Rect(rocket_panel.x + name_strip_w, rocket_panel.y, rocket_panel.w - name_strip_w, rocket_panel.h)
                rx = img_area.centerx - rimg.get_width() // 2
                ry = img_area.centery - rimg.get_height() // 2
                screen.blit(rimg, (rx, ry))
        except (ValueError, IndexError):
            pass
        screen.blit(ui_font.render("Departure", True, TEXT_SECONDARY), (60, dep_rect.y - 2))
        screen.blit(ui_font.render("Destination", True, TEXT_SECONDARY), (60, dest_rect.y - 2))
        screen.blit(ui_font.render("Ship", True, TEXT_SECONDARY), (60, ship_rect.y - 2))
        screen.blit(ui_font.render(input_labels[0], True, TEXT_SECONDARY), (60, input_rects[0].y - 2))
        screen.blit(ui_font.render(input_labels[1], True, TEXT_SECONDARY), (60, input_rects[1].y - 2))

        draw_button(btn_launch, "Calculate routes", ACCENT, ACCENT_HOVER, text_col=WHITE, border_col=ACCENT_DIM)

        for i, r in enumerate(input_rects):
            draw_input_box(r, input_texts[i], is_active=(active_input == i), placeholder=input_placeholders[i])
        if route_error:
            err_rect = Rect(270, 388, 460, 32)
            draw.rect(screen, (80, 40, 40), err_rect, border_radius=RADIUS)
            draw.rect(screen, ERROR_RED, err_rect, 1, border_radius=RADIUS)
            err_surf = small_font.render(route_error[:60] + ("..." if len(route_error) > 60 else ""), True, WARNING)
            screen.blit(err_surf, (280, 394))

        # Route summary strip (below the form + button)
        strip = Rect(40, 520, WIDTH - 80, 72)
        draw.rect(screen, BG_PANEL, strip, border_radius=RADIUS)
        draw.rect(screen, BORDER, strip, 1, border_radius=RADIUS)
        # Align summary content within the strip
        summary_mid_y = strip.y + strip.h // 2
        icon_y = summary_mid_y - 28
        text_y_main = summary_mid_y - 16
        text_y_label = summary_mid_y + 4
        if planet_imgs_strip.get(dep_selected):
            screen.blit(planet_imgs_strip[dep_selected], (strip.x + 16, icon_y))
        blit_text_clipped(dep_selected, ui_font, TEXT_PRIMARY, (strip.x + 90, text_y_main), 140)
        screen.blit(small_font.render("Departure", True, TEXT_SECONDARY), (strip.x + 90, text_y_label))

        arrow_x = strip.x + 260
        # Draw arrow (shape so it always shows regardless of font)
        ax, ay = arrow_x + 8, summary_mid_y
        draw.polygon(screen, TEXT_SECONDARY, [(ax + 12, ay), (ax, ay - 8), (ax, ay + 8)])

        if planet_imgs_strip.get(dest_selected):
            screen.blit(planet_imgs_strip[dest_selected], (arrow_x + 40, icon_y))
        blit_text_clipped(dest_selected, ui_font, TEXT_PRIMARY, (arrow_x + 114, text_y_main), 160)
        screen.blit(small_font.render("Destination", True, TEXT_SECONDARY), (arrow_x + 114, text_y_label))

        ship_x = strip.right - 280
        blit_text_clipped(_ship_display_name(ship_selected), small_font, TEXT_PRIMARY, (ship_x, text_y_main), 260)
        screen.blit(small_font.render("Ship", True, TEXT_SECONDARY), (ship_x, text_y_label))

        # Dropdowns (draw bases first, then open list on top; ship shows name + max payload)
        draw_dropdown_box(dep_rect, dep_selected, dep_open, planet_options, draw_list=False)
        draw_dropdown_box(dest_rect, dest_selected, dest_open, planet_options, draw_list=False)
        draw_dropdown_box(ship_rect, _ship_display_name(ship_selected), ship_open, ship_display_options, draw_list=False)
        if dep_open:
            draw_dropdown_box(dep_rect, dep_selected, dep_open, planet_options, draw_list=True)
        elif dest_open:
            draw_dropdown_box(dest_rect, dest_selected, dest_open, planet_options, draw_list=True)
        elif ship_open:
            draw_dropdown_box(ship_rect, _ship_display_name(ship_selected), ship_open, ship_display_options, draw_list=True)

        if _calc_in_progress:
            screen.blit(overlay_calc, (0, 0))
            draw.rect(screen, BG_PANEL, Rect(WIDTH//2 - 140, HEIGHT//2 - 40, 280, 80), border_radius=RADIUS)
            draw.rect(screen, BORDER, Rect(WIDTH//2 - 140, HEIGHT//2 - 40, 280, 80), 1, border_radius=RADIUS)
            calc_text = main_font.render("Calculating routes...", True, TEXT_PRIMARY)
            screen.blit(calc_text, calc_text.get_rect(center=(WIDTH//2, HEIGHT//2 - 10)))
            hint = small_font.render("Searching launch window", True, TEXT_SECONDARY)
            screen.blit(hint, hint.get_rect(center=(WIDTH//2, HEIGHT//2 + 20)))

    elif current_screen == "screen2":
        screen.fill(BG_DARK)
        draw_starfield()
        draw.rect(screen, BG_PANEL, Rect(0, 0, WIDTH, HEADER_H))
        draw.line(screen, BORDER, (0, HEADER_H), (WIDTH, HEADER_H), 1)
        draw_button(btn_back, "← Back", BG_PANEL, BG_CARD, text_col=TEXT_PRIMARY, border_col=BORDER)
        draw_button(btn_exit, "Exit", ERROR_RED, (200, 90, 90), text_col=WHITE, border_col=(180, 60, 60))
        t1 = title_font.render("Instructions", True, TEXT_PRIMARY)
        screen.blit(t1, t1.get_rect(center=(WIDTH // 2, HEADER_H // 2)))

        panel = Rect(40, HEADER_H + 16, WIDTH - 80, HEIGHT - HEADER_H - 100)
        draw_panel(panel, alpha=220)
        y = panel.y + 38
        blit_text_clipped("About this platform", main_font, ACCENT, (60, y), panel.w - 80)
        y += 36
        lines = [
            "This platform is a scalable route-planning and logistics tool for interplanetary",
            "trade. It helps you find fuel-efficient and time-optimal routes between refuel",
            "stations (planets, Pluto, and Ceres) within a chosen launch window.",
            "",
            "How to plan a route",
            "1. Choose departure and destination from the dropdowns.",
            "2. Select a ship (ICTB-certified). Payload must not exceed the ship's max payload.",
            "3. Enter the launch window as two dates: ddmmyyyy ddmmyyyy (e.g. 01012025 31012025).",
            "4. Enter payload mass in kg.",
            "5. Click \"Calculate routes\" to get two options: most fuel-efficient and soonest arrival.",
            "",
            "What counts as a valid trajectory",
            "A launch window is \"valid\" if there is at least one departure date between your two dates",
            "where the solver can connect your chosen departure and destination with the selected ship.",
            "If no such trajectory exists in that window, you'll see \"Flight impossible\" and should widen",
            "or shift the window.",
            "",
            "You can view past routes from the main menu and compare them.",
        ]
        for line in lines:
            if line == "":
                y += 12
            elif line == "How to plan a route":
                y += 8
                blit_text_clipped(line, main_font, ACCENT, (60, y), panel.w - 80)
                y += 34
            elif line.startswith("1.") or line.startswith("2.") or line.startswith("3.") or line.startswith("4.") or line.startswith("5."):
                blit_text_clipped(line, ui_font, TEXT_PRIMARY, (70, y), panel.w - 80)
                y += 28
            else:
                blit_text_clipped(line, small_font, TEXT_SECONDARY, (60, y), panel.w - 80)
                y += 26
        draw_button(btn_music, music_label, music_fill, music_hover_fill, text_col=music_text_col, border_col=music_border)

    elif current_screen == "screen3":
        screen.fill(BG_DARK)
        draw_starfield()
        draw.rect(screen, BG_PANEL, Rect(0, 0, WIDTH, HEADER_H))
        draw.line(screen, BORDER, (0, HEADER_H), (WIDTH, HEADER_H), 1)
        draw_button(btn_back, "← Back", BG_PANEL, BG_CARD, text_col=TEXT_PRIMARY, border_col=BORDER)
        draw_button(btn_exit, "Exit", ERROR_RED, (200, 90, 90), text_col=WHITE, border_col=(180, 60, 60))
        t1 = title_font.render("Trade simulation", True, TEXT_PRIMARY)
        screen.blit(t1, t1.get_rect(center=(WIDTH // 2, HEADER_H // 2)))

        # Sun (image if available, otherwise fallback circle)
        if sun_img and sun_img_rect:
            # Keep centered on sun_pos in case window layout changes
            sun_img_rect.center = sun_pos
            screen.blit(sun_img, sun_img_rect)
        else:
            draw.circle(screen, WARNING, sun_pos, 22)

        for p in planet_options:
            r, _ = orbit_data.get(p, (120, 1.0))
            draw_orbit(r)

        # planet positions for current animation time (if any)
        if route_anim_segments:
            t_for_orbits = route_anim_time_day * DAY_TO_SIM
        else:
            t_for_orbits = sim_time

        pos_map = {}
        for p in planet_options:
            px, py = planet_xy(p, t_for_orbits)
            pos_map[p] = (px, py)
            img = planet_imgs_sim.get(p)
            if img:
                rect = img.get_rect(center=(px, py))
                screen.blit(img, rect)
            else:
                # Fallback: simple filled circle when no image is available (no extra outline)
                draw.circle(screen, BORDER, (px, py), 7)

        # ship travel: either live route animation (from computed segments) or simple straight-line
        ship_pos = None
        if route_anim_segments:
            # find current segment based on route_anim_time_day
            seg = route_anim_segments[-1]
            for s in route_anim_segments:
                if route_anim_time_day <= s[1]:
                    seg = s
                    break
            d0, d1, b0, b1 = seg
            span = max(1e-6, d1 - d0)
            alpha = max(0.0, min(1.0, (route_anim_time_day - d0) / span))
            if b0 in pos_map and b1 in pos_map:
                a = pos_map[b0]
                b = pos_map[b1]
                sx = int(a[0] + (b[0] - a[0]) * alpha)
                sy = int(a[1] + (b[1] - a[1]) * alpha)
                ship_pos = (sx, sy)
                # draw full segment and current position
                draw.line(screen, ACCENT, a, b, 2)
                draw.circle(screen, SUCCESS, ship_pos, 7)
                r_surf = rocket_marker_font.render("R", True, WHITE)
                screen.blit(r_surf, r_surf.get_rect(center=ship_pos))
        else:
            if travel_active and travel_from in pos_map and travel_to in pos_map:
                a = pos_map[travel_from]
                b = pos_map[travel_to]
                speed = 0.30
                speed *= 1.0 / (1.0 + max(0.0, travel_payload) / 2000.0)
                travel_t += dt * speed
                if travel_t >= 1.0:
                    travel_t = 1.0
                    travel_active = False
                sx = int(a[0] + (b[0] - a[0]) * travel_t)
                sy = int(a[1] + (b[1] - a[1]) * travel_t)
                ship_pos = (sx, sy)
                draw.line(screen, ACCENT, a, ship_pos, 2)
                draw.circle(screen, SUCCESS, ship_pos, 6)
                r_surf = rocket_marker_font.render("R", True, WHITE)
                screen.blit(r_surf, r_surf.get_rect(center=ship_pos))

        info_rect = Rect(20, HEADER_H + 14, 260, 180)
        draw_panel(info_rect)
        screen.blit(small_font.render(f"From: {travel_from}", True, TEXT_PRIMARY), (36, info_rect.y + 12))
        screen.blit(small_font.render(f"To: {travel_to}", True, TEXT_PRIMARY), (36, info_rect.y + 36))
        blit_text_clipped(f"Ship: {travel_ship_name}", small_font, TEXT_SECONDARY, (36, info_rect.y + 60), info_rect.w - 24)
        screen.blit(small_font.render(f"Payload: {travel_payload:.1f} kg", True, TEXT_SECONDARY), (36, info_rect.y + 84))
        if route_anim_segments:
            start_day = route_anim_segments[0][0]
            prog = max(0.0, min(1.0, (route_anim_time_day - start_day) / max(1e-6, route_anim_total_days)))
            status = f"Animating route: {int(prog * 100)}%"
            status_color = SUCCESS if not route_animating else WARNING
        else:
            status = "Arrived at destination" if not travel_active else "En route..."
            status_color = SUCCESS if not travel_active else WARNING
        blit_text_clipped(status, ui_font, status_color, (36, info_rect.y + 108), info_rect.w - 24)
        draw_button(btn_music, music_label, music_fill, music_hover_fill, text_col=music_text_col, border_col=music_border)

    elif current_screen == "screen4" and route_result and not route_result.get("Flight impossible"):
        screen.fill(BG_DARK)
        draw_starfield()
        # Two-row header: title centered row 1, buttons centered row 2 (no overlap)
        draw.rect(screen, BG_PANEL, Rect(0, 0, WIDTH, HEADER_H_ROUTE))
        draw.line(screen, BORDER, (0, HEADER_H_ROUTE), (WIDTH, HEADER_H_ROUTE), 1)
        draw_button(btn_back, "← Back", BG_PANEL, BG_CARD, text_col=TEXT_PRIMARY, border_col=BORDER)
        draw_button(btn_exit, "Exit", ERROR_RED, (200, 90, 90), text_col=WHITE, border_col=(180, 60, 60))
        t1 = title_font.render("Route options", True, TEXT_PRIMARY)
        screen.blit(t1, t1.get_rect(center=(WIDTH // 2, _route_title_y)))
        t2 = small_font.render(f"{travel_from} → {travel_to}", True, TEXT_SECONDARY)
        screen.blit(t2, t2.get_rect(center=(WIDTH // 2, _route_subtitle_y)))

        draw_button(btn_efficient, "Most fuel efficient", ACCENT if route_view == 0 else BG_CARD, ACCENT_HOVER if route_view == 0 else (60, 64, 80), text_col=WHITE if route_view == 0 else TEXT_PRIMARY, border_col=ACCENT_DIM if route_view == 0 else BORDER)
        draw_button(btn_soonest, "Soonest arrival", ACCENT if route_view == 1 else BG_CARD, ACCENT_HOVER if route_view == 1 else (60, 64, 80), text_col=WHITE if route_view == 1 else TEXT_PRIMARY, border_col=ACCENT_DIM if route_view == 1 else BORDER)
        draw_button(btn_animate, "Animate route", BG_PANEL, BG_CARD, text_col=TEXT_PRIMARY, border_col=BORDER_FOCUS)

        opt_key = "Efficient flight parameters" if route_view == 0 else "Soonest arrival flight parameters"
        opt = route_result.get(opt_key) or {}
        # Parameters panel (below header, with spacing)
        params_rect = Rect(20, ROUTE_CONTENT_TOP, 420, 380)
        draw_panel(params_rect)
        y = params_rect.y + 16
        screen.blit(small_font.render("Flight parameters", True, TEXT_SECONDARY), (36, y))
        y += 26
        for k, v in opt.items():
            if k.startswith("_"):
                continue
            if isinstance(v, dict):
                blit_text_clipped(k, ui_font, ACCENT, (36, y), params_rect.w - 40)
                y += 24
                for kk, vv in v.items():
                    if y > params_rect.bottom - 30:
                        screen.blit(small_font.render("…", True, TEXT_SECONDARY), (36, y))
                        break
                    blit_text_clipped(f"  {kk}: {vv}", small_font, TEXT_PRIMARY, (44, y), params_rect.w - 52)
                    y += 22
                y += 6
            else:
                if y > params_rect.bottom - 26:
                    screen.blit(small_font.render("…", True, TEXT_SECONDARY), (36, y))
                    break
                blit_text_clipped(f"{k}: {v}", small_font, TEXT_PRIMARY, (36, y), params_rect.w - 40)
                y += 24

        # Flight path panel (fills right side)
        path_rect = Rect(420, ROUTE_CONTENT_TOP, WIDTH - 440, 380)
        draw_panel(path_rect)
        screen.blit(small_font.render("Flight path", True, TEXT_SECONDARY), (path_rect.x + 16, path_rect.y + 14))
        waypoints = opt.get("_waypoints", [])
        if waypoints:
            cx, cy = path_rect.centerx, path_rect.centery + 24
            scale = 150 / 350.0
            # Draw orbital tracks
            for p in planet_options:
                r, spd = orbit_data.get(p, (120, 1.0))
                draw.ellipse(screen, (50, 54, 70), (cx - r * scale, cy - r * scale * 0.7, r * 2 * scale, r * 2 * 0.7 * scale), 1)
            # Compute waypoint positions along the route
            pts = []
            bodies = []
            for day, body in waypoints:
                if body in orbit_data:
                    r, spd = orbit_data[body]
                    ang = day * DAY_TO_SIM * spd
                    px = cx + cos(ang) * r * scale
                    py = cy + sin(ang) * r * scale * 0.7
                    pts.append((int(px), int(py)))
                    bodies.append(body)
            # Route polyline
            for i in range(len(pts) - 1):
                draw.line(screen, ACCENT, pts[i], pts[i + 1], 3)
            # Draw planets (or fallback circles) at waypoints (no hitbox rings)
            for i, (pos, body) in enumerate(zip(pts, bodies)):
                img = planet_imgs_sim.get(body)
                if img:
                    rect = img.get_rect(center=pos)
                    screen.blit(img, rect)
                else:
                    # Simple filled marker for waypoint when no image
                    draw.circle(screen, BORDER, pos, 7)
            if len(pts) >= 2:
                screen.blit(small_font.render("Departure", True, SUCCESS), (path_rect.x + 12, path_rect.bottom - 50))
                screen.blit(small_font.render("Arrival", True, ERROR_RED), (path_rect.right - 70, path_rect.bottom - 50))
        draw_button(btn_music, music_label, music_fill, music_hover_fill, text_col=music_text_col, border_col=music_border)

    elif current_screen == "screen5":
        screen.fill(BG_DARK)
        draw_starfield()
        draw.rect(screen, BG_PANEL, Rect(0, 0, WIDTH, HEADER_H))
        draw.line(screen, BORDER, (0, HEADER_H), (WIDTH, HEADER_H), 1)
        draw_button(btn_back, "← Back", BG_PANEL, BG_CARD, text_col=TEXT_PRIMARY, border_col=BORDER)
        draw_button(btn_exit, "Exit", ERROR_RED, (200, 90, 90), text_col=WHITE, border_col=(180, 60, 60))
        t1 = title_font.render("Past routes", True, TEXT_PRIMARY)
        screen.blit(t1, t1.get_rect(center=(WIDTH // 2, HEADER_H // 2 - 10)))
        t2 = small_font.render("Click a route to view details and compare", True, TEXT_SECONDARY)
        screen.blit(t2, t2.get_rect(center=(WIDTH // 2, HEADER_H // 2 + 14)))

        if not past_routes_list:
            empty_rect = Rect(80, HEADER_H + 24, WIDTH - 160, 120)
            draw_panel(empty_rect)
            t_empty1 = ui_font.render("No saved routes yet", True, TEXT_SECONDARY)
            t_empty2 = small_font.render("Plan a route from the menu to see it here", True, TEXT_SECONDARY)
            screen.blit(t_empty1, t_empty1.get_rect(center=(empty_rect.centerx, empty_rect.y + 40)))
            screen.blit(t_empty2, t_empty2.get_rect(center=(empty_rect.centerx, empty_rect.y + 78)))
        else:
            for i, r in enumerate(past_routes_list):
                rect = Rect(80, HEADER_H + 20 + i * 48, WIDTH - 160, 44)
                hover = rect.collidepoint((mx, my))
                fill = (BG_CARD[0] + 15, BG_CARD[1] + 15, BG_CARD[2] + 15) if hover else BG_CARD
                draw.rect(screen, fill, rect, border_radius=RADIUS)
                draw.rect(screen, BORDER_FOCUS if hover else BORDER, rect, 1, border_radius=RADIUS)
                txt = f"{r.get('origin', '?')}  →  {r.get('destination', '?')}  •  {r.get('ship', '?')}  •  {r.get('payload_kg', 0)} kg"
                blit_text_clipped(txt, ui_font, TEXT_PRIMARY, (96, rect.y + (rect.h - ui_font.get_height()) // 2), rect.w - 120)
        draw_button(btn_music, music_label, music_fill, music_hover_fill, text_col=music_text_col, border_col=music_border)

    elif current_screen == "screen6":
        # Rocket specs screen
        screen.fill(BG_DARK)
        draw_starfield()
        draw.rect(screen, BG_PANEL, Rect(0, 0, WIDTH, HEADER_H))
        draw.line(screen, BORDER, (0, HEADER_H), (WIDTH, HEADER_H), 1)
        draw_button(btn_back, "← Back", BG_PANEL, BG_CARD, text_col=TEXT_PRIMARY, border_col=BORDER)
        draw_button(btn_exit, "Exit", ERROR_RED, (200, 90, 90), text_col=WHITE, border_col=(180, 60, 60))
        t1 = title_font.render("Rocket specifications", True, TEXT_PRIMARY)
        screen.blit(t1, t1.get_rect(center=(WIDTH // 2, HEADER_H // 2 - 10)))
        t2 = small_font.render("ICTB-certified interplanetary ships", True, TEXT_SECONDARY)
        screen.blit(t2, t2.get_rect(center=(WIDTH // 2, HEADER_H // 2 + 14)))

        panel = Rect(40, HEADER_H + 16, WIDTH - 80, HEIGHT - HEADER_H - 100)
        draw_panel(panel, alpha=220)

        # Column headings (spaced so numbers don't overlap)
        y = panel.y + 18
        x_name = panel.x + 170
        x_dry = panel.x + 410
        x_fuel = panel.x + 540
        x_isp = panel.x + 690
        x_payload = panel.x + 860
        screen.blit(small_font.render("Rocket", True, TEXT_SECONDARY), (x_name, y))
        screen.blit(small_font.render("Dry mass (kg)", True, TEXT_SECONDARY), (x_dry, y))
        screen.blit(small_font.render("Fuel (kg)", True, TEXT_SECONDARY), (x_fuel, y))
        screen.blit(small_font.render("Isp (km/s)", True, TEXT_SECONDARY), (x_isp, y))
        screen.blit(small_font.render("Max payload (kg)", True, TEXT_SECONDARY), (x_payload, y))
        y += 28

        # Rows: rocket image + name + specs
        try:
            import ships as _sh
        except Exception:
            _sh = None

        row_h = 70
        for idx, name in enumerate(ship_options):
            row_top = y + idx * row_h
            row_rect = Rect(panel.x + 8, row_top, panel.w - 16, row_h - 8)
            draw.rect(screen, BG_CARD, row_rect, border_radius=RADIUS)
            draw.rect(screen, BORDER, row_rect, 1, border_radius=RADIUS)

            # Rocket image on the left side of the row
            img = rocket_imgs[idx] if idx < len(rocket_imgs) else None
            if img:
                ih = min(img.get_height(), row_h - 16)
                scale = ih / img.get_height()
                iw = int(img.get_width() * scale)
                if iw > 120:
                    scale = 120 / img.get_width()
                    iw = 120
                    ih = int(img.get_height() * scale)
                thumb = transform.smoothscale(img, (iw, ih)) if (iw != img.get_width() or ih != img.get_height()) else img
                ix = row_rect.x + 18
                iy = row_rect.y + (row_rect.h - ih) // 2
                screen.blit(thumb, (ix, iy))
            else:
                ix = row_rect.x + 18

            # Rocket name next to the image
            name_x = ix + 140
            blit_text_clipped(name, ui_font, TEXT_PRIMARY, (name_x, row_rect.y + 12), 220)

            # Specs from ships.py
            spec = _sh.get_ship_spec(name) if _sh is not None else None
            if spec:
                dry = f"{spec['dry_mass_kg']:,}"
                fuel = f"{spec['fuel_capacity_kg']:,}"
                isp = f"{spec['Isp_km_s']:.2f}"
                max_pl = f"{spec['max_payload_kg']:,}"
                screen.blit(small_font.render(dry, True, TEXT_PRIMARY), (x_dry, row_rect.y + 30))
                screen.blit(small_font.render(fuel, True, TEXT_PRIMARY), (x_fuel, row_rect.y + 30))
                screen.blit(small_font.render(isp, True, TEXT_PRIMARY), (x_isp, row_rect.y + 30))
                screen.blit(small_font.render(max_pl, True, TEXT_PRIMARY), (x_payload, row_rect.y + 30))

        draw_button(btn_music, music_label, music_fill, music_hover_fill, text_col=music_text_col, border_col=music_border)

    # Optional: show mouse coords only on screen3 (simulation) for debugging
    if current_screen == "screen3":
        screen.blit(coord_font.render(f"({mx}, {my})", True, TEXT_SECONDARY), (10, 10))

    display.flip()

quit()

'''Sources used: 
  1.  https://www.youtube.com/watch?v=6bHwWFOz4Ww
  2.  https://trinket.io/glowscript/63cb9fd49d
  3.  https://www.youtube.com/watch?v=yRKALsvGAGE
  4.  https://stackoverflow.com/questions/45441885/how-can-i-create-a-dropdown-menu-from-a-list-in-tkinter
  5.  https://www.youtube.com/watch?v=WTLPmUHTPqo
  6.  https://stackoverflow.com/questions/19877900/tips-on-adding-creating-a-drop-down-selection-box-in-pygame
  7.  https://www.youtube.com/watch?v=eJc6fEX-0r0
  8.  

'''