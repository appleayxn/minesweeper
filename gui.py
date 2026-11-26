"""
Minesweeper - Algorithms and Programming 1 - UFAZ
Team: Zeynalzada Ayxan, Maharramli Anvar, Qurbanli Elton,
      Nuruzada Nihat, Hamzayev Altair
File: gui.py
Role: OPTIONAL EXTRA - graphical version of the game with pygame
      (approved by the teacher; written with the help of an AI assistant).

This file adds ONLY the interface and the animations. All the rules of the
game come from the text version: new_state, reveal, toggle_flag, check_win,
check_loss, find_hint (game_logic.py), neighbours and LEVELS (board.py),
and the best times of scores.py (same file scores.txt).

Run with:   pip install pygame      (once)
            python gui.py

Controls:   left click = reveal, right click = flag,
            H = hint, D = debug (show the mines), T = theme,
            R = new game, Esc = back to the menu.
"""

import math
import random
import time

import pygame

from board import LEVELS, LEVEL_NAMES, neighbours
from game_logic import new_state, reveal, toggle_flag, check_win, check_loss, find_hint
from scores import SCORES_FILE, board_key, load_scores, save_scores, update_scores

# ---------------------------------------------------------------- constants
WIDTH = 640
HEIGHT = 800
FPS = 60
BOARD_TOP = 130            # y where the board area starts
BOARD_AREA_W = 600
BOARD_AREA_H = 610

REVEAL_TIME = 0.22         # seconds for one cell to open
WAVE_DELAY = 0.03          # delay between two "rings" of the opening wave
FLAG_TIME = 0.45           # seconds of the flag "pop"
THEME_FADE = 0.35          # seconds to change from one theme to another

# Four colour themes. Every theme is a dictionary of colours (r, g, b).
THEMES = [
    {   # the grey Windows look
        "name": "Classic", "style": "bevel",
        "bg": (192, 192, 192), "panel": (192, 192, 192), "panel_text": (0, 0, 0),
        "hidden": (198, 198, 198), "hidden_alt": (198, 198, 198), "hover": (214, 214, 214),
        "light": (255, 255, 255), "dark": (128, 128, 128),
        "revealed": (189, 189, 189), "revealed_alt": (189, 189, 189), "grid": (128, 128, 128),
        "text": (0, 0, 0), "accent": (0, 0, 128), "flag": (230, 0, 0), "mine": (0, 0, 0),
        "counter_bg": (0, 0, 0), "counter_fg": (255, 0, 0),
        "numbers": [(0, 0, 255), (0, 128, 0), (255, 0, 0), (0, 0, 128),
                    (128, 0, 0), (0, 128, 128), (0, 0, 0), (128, 128, 128)],
    },
    {   # dark mode
        "name": "Dark", "style": "flat",
        "bg": (22, 24, 31), "panel": (34, 37, 46), "panel_text": (220, 223, 228),
        "hidden": (58, 63, 79), "hidden_alt": (54, 59, 74), "hover": (82, 89, 110),
        "light": (78, 84, 102), "dark": (30, 32, 40),
        "revealed": (30, 32, 40), "revealed_alt": (27, 29, 36), "grid": (28, 30, 38),
        "text": (220, 223, 228), "accent": (97, 175, 239), "flag": (239, 83, 80), "mine": (15, 15, 20),
        "counter_bg": (24, 26, 33), "counter_fg": (229, 192, 123),
        "numbers": [(97, 175, 239), (152, 195, 121), (224, 108, 117), (198, 120, 221),
                    (229, 192, 123), (86, 182, 194), (220, 223, 228), (130, 137, 151)],
    },
    {   # green grass, like the Google version
        "name": "Green", "style": "flat",
        "bg": (74, 117, 44), "panel": (74, 117, 44), "panel_text": (255, 255, 255),
        "hidden": (170, 215, 81), "hidden_alt": (162, 209, 73), "hover": (191, 225, 125),
        "light": (191, 225, 125), "dark": (135, 175, 58),
        "revealed": (229, 194, 159), "revealed_alt": (215, 184, 153), "grid": (200, 170, 140),
        "text": (255, 255, 255), "accent": (255, 213, 79), "flag": (242, 54, 7), "mine": (40, 40, 40),
        "counter_bg": (56, 92, 32), "counter_fg": (255, 255, 255),
        "numbers": [(25, 118, 210), (56, 142, 60), (211, 47, 47), (123, 31, 162),
                    (255, 143, 0), (0, 151, 167), (66, 66, 66), (158, 158, 158)],
    },
    {   # blue sea
        "name": "Ocean", "style": "flat",
        "bg": (10, 25, 47), "panel": (16, 38, 68), "panel_text": (220, 235, 250),
        "hidden": (30, 90, 150), "hidden_alt": (35, 100, 165), "hover": (64, 138, 205),
        "light": (70, 140, 205), "dark": (18, 60, 105),
        "revealed": (200, 225, 245), "revealed_alt": (188, 216, 240), "grid": (160, 195, 225),
        "text": (220, 235, 250), "accent": (64, 196, 255), "flag": (255, 112, 67), "mine": (12, 30, 55),
        "counter_bg": (8, 20, 38), "counter_fg": (64, 196, 255),
        "numbers": [(21, 101, 192), (0, 137, 123), (229, 57, 53), (94, 53, 177),
                    (239, 108, 0), (0, 131, 143), (38, 50, 56), (96, 125, 139)],
    },
]

CONFETTI_COLORS = [(244, 67, 54), (255, 193, 7), (76, 175, 80), (33, 150, 243),
                   (156, 39, 176), (255, 255, 255)]


# ---------------------------------------------------------------- small maths helpers
def clamp(x, low, high):
    """Keep x between low and high.

    Parameters:
        x (float): the value
        low (float): smallest value allowed
        high (float): biggest value allowed

    Returns:
        float: the value inside [low, high]
    """
    if x < low:
        return low
    if x > high:
        return high
    return x


def lerp(a, b, t):
    """Go from a to b: t = 0 gives a, t = 1 gives b.

    Parameters:
        a (float): start value
        b (float): end value
        t (float): progress between 0 and 1

    Returns:
        float: the value between a and b
    """
    return a + (b - a) * t


def lerp_color(c1, c2, t):
    """Mix two colours: t = 0 gives c1, t = 1 gives c2.

    Parameters:
        c1 (tuple): first colour (r, g, b)
        c2 (tuple): second colour (r, g, b)
        t (float): progress between 0 and 1

    Returns:
        tuple: the mixed colour
    """
    return (int(lerp(c1[0], c2[0], t)), int(lerp(c1[1], c2[1], t)), int(lerp(c1[2], c2[2], t)))


def lighter(color, amount):
    """Make a colour lighter (amount > 0) or darker (amount < 0).

    Parameters:
        color (tuple): colour (r, g, b)
        amount (float): between -1 and 1

    Returns:
        tuple: the new colour
    """
    if amount >= 0:
        return lerp_color(color, (255, 255, 255), amount)
    return lerp_color(color, (0, 0, 0), -amount)


def ease_out_cubic(t):
    """Fast at the start, slow at the end (0 -> 1).

    Parameters:
        t (float): progress between 0 and 1

    Returns:
        float: eased progress
    """
    t = clamp(t, 0, 1)
    return 1 - (1 - t) ** 3


def ease_out_back(t):
    """Goes a little past 1 then comes back: a small "pop" effect.

    Parameters:
        t (float): progress between 0 and 1

    Returns:
        float: eased progress
    """
    t = clamp(t, 0, 1)
    c1 = 1.70158
    c3 = c1 + 1
    return 1 + c3 * (t - 1) ** 3 + c1 * (t - 1) ** 2


def ease_out_elastic(t):
    """Bounces like a spring before stopping at 1.

    Parameters:
        t (float): progress between 0 and 1

    Returns:
        float: eased progress
    """
    t = clamp(t, 0, 1)
    if t == 0 or t == 1:
        return t
    return 2 ** (-10 * t) * math.sin((t * 10 - 0.75) * (2 * math.pi) / 3) + 1


# ---------------------------------------------------------------- app state
def new_app(screen):
    """Create the dictionary with everything the window needs.

    Parameters:
        screen (pygame.Surface): the window

    Returns:
        dict: the application state
    """
    return {
        "screen": screen,
        "mode": "menu",                 # "menu" or "game"
        "theme": 0, "old_theme": 0, "theme_time": -10.0,
        "fonts": {}, "text_cache": {},
        "level": 1, "custom": [10, 10, 15], "safe_start": False,
        "sel_x": 0.0, "toggle_x": 0.0,
        "scores": load_scores(SCORES_FILE),
        "hover": {}, "buttons": [],
        "particles": [], "menu_tiles": [],
        "toast": None,
        "game": None,
    }


def font(app, size, bold):
    """Return a font, created only once.

    Parameters:
        app (dict): the application state
        size (int): size of the letters
        bold (bool): True for bold letters

    Returns:
        pygame.font.Font: the font
    """
    key = (size, bold)
    if key not in app["fonts"]:
        app["fonts"][key] = pygame.font.SysFont("segoeui,arial,dejavusans", size, bold)
    return app["fonts"][key]


def text_surface(app, text, size, color, bold):
    """Render a text once and keep it in a cache (faster).

    Parameters:
        app (dict): the application state
        text (str): the text
        size (int): size of the letters
        color (tuple): colour of the text
        bold (bool): bold or not

    Returns:
        pygame.Surface: the picture of the text
    """
    key = (text, size, color, bold)
    if key not in app["text_cache"]:
        if len(app["text_cache"]) > 600:
            app["text_cache"] = {}
        app["text_cache"][key] = font(app, size, bold).render(text, True, color)
    return app["text_cache"][key]


def draw_text(app, surf, text, size, color, center, bold):
    """Draw a text centred on a point.

    Parameters:
        app (dict): the application state
        surf (pygame.Surface): where to draw
        text (str): the text
        size (int): size of the letters
        color (tuple): colour
        center (tuple): (x, y) of the centre
        bold (bool): bold or not

    Returns:
        pygame.Rect: the place of the text
    """
    picture = text_surface(app, text, size, color, bold)
    rect = picture.get_rect(center=(int(center[0]), int(center[1])))
    surf.blit(picture, rect)
    return rect


def colors(app, now):
    """Colours of the current theme. When the theme changes, the old and the
    new colours are mixed for a smooth transition.

    Parameters:
        app (dict): the application state
        now (float): current time

    Returns:
        dict: the theme with the mixed colours
    """
    new = THEMES[app["theme"]]
    t = ease_out_cubic((now - app["theme_time"]) / THEME_FADE)
    if t >= 1:
        return new
    old = THEMES[app["old_theme"]]
    mixed = {"name": new["name"], "style": new["style"]}
    for key in new:
        if key == "numbers":
            mixed[key] = [lerp_color(old[key][i], new[key][i], t) for i in range(8)]
        elif key not in ("name", "style"):
            mixed[key] = lerp_color(old[key], new[key], t)
    return mixed


def change_theme(app, now):
    """Go to the next theme (with a fade).

    Parameters:
        app (dict): the application state
        now (float): current time

    Returns:
        None
    """
    app["old_theme"] = app["theme"]
    app["theme"] = (app["theme"] + 1) % len(THEMES)
    app["theme_time"] = now


def show_toast(app, text, now):
    """Show a short message at the bottom of the window.

    Parameters:
        app (dict): the application state
        text (str): the message
        now (float): current time

    Returns:
        None
    """
    app["toast"] = (text, now)


def hover_amount(app, key, target, dt):
    """Move a hover value smoothly to 0 or 1 (for buttons and cells).

    Parameters:
        app (dict): the application state
        key: name of the thing under the mouse
        target (float): 1 if the mouse is on it, else 0
        dt (float): time since the last frame

    Returns:
        float: the smooth value between 0 and 1
    """
    value = app["hover"].get(key, 0.0)
    value = value + (target - value) * clamp(dt * 14, 0, 1)
    if value < 0.01 and target == 0:
        if key in app["hover"]:
            del app["hover"][key]
        return 0.0
    app["hover"][key] = value
    return value


# ---------------------------------------------------------------- game start
def current_settings(app):
    """Size and number of mines chosen in the menu.

    Parameters:
        app (dict): the application state

    Returns:
        tuple: (rows, cols, nb_mines)
    """
    if app["level"] == 4:
        return app["custom"][0], app["custom"][1], app["custom"][2]
    size = LEVELS[app["level"]]
    return size[0], size[1], size[2]


def start_game(app, now):
    """Start a new game with the settings of the menu.

    Parameters:
        app (dict): the application state
        now (float): current time

    Returns:
        None
    """
    rows, cols, nb_mines = current_settings(app)
    seed = random.randint(1, 999999)
    state = new_state(rows, cols, nb_mines, seed)      # same rules as the text game
    state["safe_start"] = app["safe_start"]
    cell = int(min(56, BOARD_AREA_W / cols, BOARD_AREA_H / rows))
    x0 = (WIDTH - cell * cols) // 2
    y0 = BOARD_TOP + (BOARD_AREA_H - cell * rows) // 2
    app["game"] = {
        "state": state, "cell": cell, "x0": x0, "y0": y0,
        "reveal_anim": {}, "flag_anim": {}, "mine_anim": {},
        "start": None, "end": None, "end_time": None,
        "shake": None, "debug": False, "debug_t": 0.0,
        "hint": None, "pressed": False, "record": False,
        "overlay_time": None,
    }
    app["particles"] = []
    app["mode"] = "game"


def cell_at(app, pos):
    """Find the cell under the mouse.

    Parameters:
        app (dict): the application state
        pos (tuple): (x, y) of the mouse

    Returns:
        tuple: (row, col) or None if the mouse is not on the board
    """
    g = app["game"]
    col = (pos[0] - g["x0"]) // g["cell"]
    row = (pos[1] - g["y0"]) // g["cell"]
    if 0 <= row < g["state"]["rows"] and 0 <= col < g["state"]["cols"]:
        return (int(row), int(col))
    return None


def cell_center(app, cell):
    """Centre of a cell on the screen.

    Parameters:
        app (dict): the application state
        cell (tuple): (row, col)

    Returns:
        tuple: (x, y)
    """
    g = app["game"]
    return (g["x0"] + cell[1] * g["cell"] + g["cell"] / 2,
            g["y0"] + cell[0] * g["cell"] + g["cell"] / 2)


# ---------------------------------------------------------------- game actions
def click_reveal(app, cell, now):
    """Left click: reveal a cell with the function of the text version,
    then start the opening wave animation.

    Parameters:
        app (dict): the application state
        cell (tuple): (row, col)
        now (float): current time

    Returns:
        None
    """
    g = app["game"]
    state = g["state"]
    before = set(state["revealed"])
    message = reveal(cell, state)                       # the real rules
    if message != "":
        show_toast(app, message, now)
        return
    if g["start"] is None:
        g["start"] = now                                # the timer starts
    for opened in state["revealed"] - before:
        distance = max(abs(opened[0] - cell[0]), abs(opened[1] - cell[1]))
        g["reveal_anim"][opened] = now + distance * WAVE_DELAY
    if check_loss(state):
        finish_game(app, False, now)
    elif check_win(state):
        finish_game(app, True, now)


def click_flag(app, cell, now):
    """Right click: put or remove a flag, with a "pop" animation.

    Parameters:
        app (dict): the application state
        cell (tuple): (row, col)
        now (float): current time

    Returns:
        None
    """
    g = app["game"]
    message = toggle_flag(cell, g["state"])             # the real rules
    if message != "":
        show_toast(app, message, now)
        return
    g["flag_anim"][cell] = now


def finish_game(app, won, now):
    """End of the game: start the win or loss animations, save the time.

    Parameters:
        app (dict): the application state
        won (bool): True if the player won
        now (float): current time

    Returns:
        None
    """
    g = app["game"]
    state = g["state"]
    state["game_over"] = True
    state["won"] = won
    g["end"] = "win" if won else "lose"
    g["end_time"] = now
    g["seconds"] = int(now - g["start"]) if g["start"] is not None else 0
    origin = state["hit_mine"]
    if origin is None:
        origin = (state["rows"] // 2, state["cols"] // 2)
    # the mines appear one after the other, the nearest first
    others = []
    for m in state["mines"]:
        if m != state["hit_mine"]:
            others.append((max(abs(m[0] - origin[0]), abs(m[1] - origin[1])), m))
    others.sort()
    step = 0.045
    if len(others) > 0:
        step = min(0.045, 1.5 / len(others))
    first = 0.35 if not won else 0.15
    for i in range(len(others)):
        g["mine_anim"][others[i][1]] = now + first + i * step
    g["overlay_time"] = now + first + len(others) * step + 0.35
    if won:
        rows, cols, nb_mines = state["rows"], state["cols"], state["nb_mines"]
        key = board_key(rows, cols, nb_mines)
        if update_scores(app["scores"], key, g["seconds"]):
            save_scores(app["scores"], SCORES_FILE)
            g["record"] = True
        add_confetti(app)
    else:
        g["mine_anim"][state["hit_mine"]] = now
        g["shake"] = now
        x, y = cell_center(app, state["hit_mine"])
        add_explosion(app, x, y)


def use_hint(app, now):
    """H key: show a safe cell (find_hint of the text version).

    Parameters:
        app (dict): the application state
        now (float): current time

    Returns:
        None
    """
    g = app["game"]
    if g["state"]["first_move"]:
        show_toast(app, "Reveal a first cell before asking for a hint.", now)
        return
    cell = find_hint(g["state"])
    if cell is not None:
        g["hint"] = (cell, now)


# ---------------------------------------------------------------- particles
def add_explosion(app, x, y):
    """Sparks and smoke when a mine explodes.

    Parameters:
        app (dict): the application state
        x (float): x of the explosion
        y (float): y of the explosion

    Returns:
        None
    """
    for i in range(70):
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(80, 520)
        life = random.uniform(0.4, 1.1)
        color = random.choice([(255, 235, 59), (255, 152, 0), (244, 67, 54), (255, 255, 255)])
        app["particles"].append({"kind": "spark", "x": x, "y": y,
                                 "vx": math.cos(angle) * speed, "vy": math.sin(angle) * speed,
                                 "life": life, "max": life, "color": color,
                                 "size": random.uniform(2, 5)})
    for i in range(18):
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(20, 90)
        life = random.uniform(0.8, 1.6)
        app["particles"].append({"kind": "smoke", "x": x, "y": y,
                                 "vx": math.cos(angle) * speed, "vy": math.sin(angle) * speed - 40,
                                 "life": life, "max": life, "color": (90, 90, 90),
                                 "size": random.uniform(10, 22)})


def add_confetti(app):
    """Confetti falling from the top of the window when the player wins.

    Parameters:
        app (dict): the application state

    Returns:
        None
    """
    for i in range(170):
        life = random.uniform(2.2, 3.8)
        app["particles"].append({"kind": "confetti",
                                 "x": random.uniform(0, WIDTH), "y": random.uniform(-300, -10),
                                 "vx": random.uniform(-60, 60), "vy": random.uniform(120, 260),
                                 "life": life, "max": life,
                                 "color": random.choice(CONFETTI_COLORS),
                                 "size": random.uniform(5, 10),
                                 "rot": random.uniform(0, 6.28), "vr": random.uniform(-8, 8)})


def update_particles(app, dt):
    """Move the particles and remove the dead ones.

    Parameters:
        app (dict): the application state
        dt (float): time since the last frame

    Returns:
        None
    """
    alive = []
    for p in app["particles"]:
        p["life"] = p["life"] - dt
        if p["life"] <= 0:
            continue
        if p["kind"] == "spark":
            p["vy"] = p["vy"] + 700 * dt          # gravity
            p["vx"] = p["vx"] * (1 - 1.5 * dt)
        elif p["kind"] == "smoke":
            p["size"] = p["size"] + 18 * dt
        else:
            p["vx"] = p["vx"] + math.sin(p["life"] * 4) * 30 * dt
            p["rot"] = p["rot"] + p["vr"] * dt
        p["x"] = p["x"] + p["vx"] * dt
        p["y"] = p["y"] + p["vy"] * dt
        alive.append(p)
    app["particles"] = alive


def draw_particles(app, surf):
    """Draw all the particles.

    Parameters:
        app (dict): the application state
        surf (pygame.Surface): where to draw

    Returns:
        None
    """
    for p in app["particles"]:
        fade = clamp(p["life"] / p["max"], 0, 1)
        if p["kind"] == "spark":
            color = lerp_color((60, 20, 0), p["color"], fade)
            pygame.draw.circle(surf, color, (int(p["x"]), int(p["y"])), max(1, int(p["size"] * fade)))
        elif p["kind"] == "smoke":
            size = int(p["size"])
            blob = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            pygame.draw.circle(blob, (80, 80, 80, int(90 * fade)), (size, size), size)
            surf.blit(blob, (p["x"] - size, p["y"] - size))
        else:
            w = p["size"]
            h = p["size"] * abs(math.cos(p["rot"])) * 0.6 + 1
            piece = pygame.Surface((int(w) + 1, int(h) + 1), pygame.SRCALPHA)
            piece.fill(p["color"] + (int(255 * min(1, fade * 2)),))
            piece = pygame.transform.rotate(piece, math.degrees(p["rot"]))
            surf.blit(piece, (p["x"], p["y"]))


# ---------------------------------------------------------------- drawing pieces
def draw_mine(surf, center, size, body):
    """Draw a mine: a round body, 8 spikes and a small light reflection.

    Parameters:
        surf (pygame.Surface): where to draw
        center (tuple): (x, y)
        size (float): size of the cell
        body (tuple): colour of the mine

    Returns:
        None
    """
    x, y = center
    radius = size * 0.24
    for i in range(8):
        angle = i * math.pi / 4
        x2 = x + math.cos(angle) * radius * 1.55
        y2 = y + math.sin(angle) * radius * 1.55
        pygame.draw.line(surf, body, (x, y), (x2, y2), max(2, int(size * 0.07)))
    pygame.draw.circle(surf, body, (int(x), int(y)), int(radius))
    pygame.draw.circle(surf, (255, 255, 255), (int(x - radius * 0.35), int(y - radius * 0.35)),
                       max(1, int(radius * 0.28)))


def draw_flag(surf, center, size, scale, flag_color, pole_color):
    """Draw a flag (pole, red triangle and base), scaled for the animation.

    Parameters:
        surf (pygame.Surface): where to draw
        center (tuple): (x, y)
        size (float): size of the cell
        scale (float): 0 = invisible, 1 = normal size
        flag_color (tuple): colour of the cloth
        pole_color (tuple): colour of the pole

    Returns:
        None
    """
    if scale <= 0.02:
        return
    s = size * scale
    x, y = center
    top = y - s * 0.32
    bottom = y + s * 0.24
    pygame.draw.line(surf, pole_color, (x + s * 0.06, top), (x + s * 0.06, bottom), max(2, int(s * 0.07)))
    pygame.draw.polygon(surf, flag_color, [(x + s * 0.08, top), (x - s * 0.26, top + s * 0.14),
                                           (x + s * 0.08, top + s * 0.28)])
    pygame.draw.rect(surf, pole_color, (int(x - s * 0.18), int(bottom), int(s * 0.46), max(2, int(s * 0.08))))


def draw_bevel(surf, rect, base, light, dark, width):
    """Draw a raised 3D square, like the old Windows game.

    Parameters:
        surf (pygame.Surface): where to draw
        rect (pygame.Rect): the square
        base (tuple): main colour
        light (tuple): colour of the top-left border
        dark (tuple): colour of the bottom-right border
        width (int): width of the border

    Returns:
        None
    """
    pygame.draw.rect(surf, base, rect)
    for i in range(width):
        pygame.draw.line(surf, light, (rect.left + i, rect.top + i), (rect.right - 1 - i, rect.top + i))
        pygame.draw.line(surf, light, (rect.left + i, rect.top + i), (rect.left + i, rect.bottom - 1 - i))
        pygame.draw.line(surf, dark, (rect.left + i, rect.bottom - 1 - i), (rect.right - 1 - i, rect.bottom - 1 - i))
        pygame.draw.line(surf, dark, (rect.right - 1 - i, rect.top + i), (rect.right - 1 - i, rect.bottom - 1 - i))


def draw_hidden(surf, rect, col, checker, hover):
    """Draw a hidden cell in the style of the theme.

    Parameters:
        surf (pygame.Surface): where to draw
        rect (pygame.Rect): the cell
        col (dict): colours of the theme
        checker (int): 0 or 1, for the chess-board effect
        hover (float): 0 to 1, how much the mouse is over the cell

    Returns:
        None
    """
    if col["style"] == "bevel":
        base = lerp_color(col["hidden"], col["hover"], hover)
        draw_bevel(surf, rect, base, col["light"], col["dark"], max(2, rect.width // 12))
        return
    base = col["hidden"] if checker == 0 else col["hidden_alt"]
    base = lerp_color(base, col["hover"], hover)
    inner = rect.inflate(-2, -2)
    radius = max(3, rect.width // 6)
    pygame.draw.rect(surf, lighter(base, -0.18), inner.move(0, 2), border_radius=radius)
    pygame.draw.rect(surf, base, inner, border_radius=radius)
    shine = inner.inflate(-int(inner.width / 3), -int(inner.height / 1.6))
    shine.top = inner.top + max(2, inner.height // 10)
    pygame.draw.rect(surf, lighter(base, 0.12), shine, border_radius=radius)


def draw_revealed(surf, rect, col, checker):
    """Draw the background of a revealed cell.

    Parameters:
        surf (pygame.Surface): where to draw
        rect (pygame.Rect): the cell
        col (dict): colours of the theme
        checker (int): 0 or 1, for the chess-board effect

    Returns:
        None
    """
    base = col["revealed"] if checker == 0 else col["revealed_alt"]
    if col["style"] == "bevel":
        pygame.draw.rect(surf, base, rect)
        pygame.draw.rect(surf, col["grid"], rect, 1)
        return
    pygame.draw.rect(surf, base, rect.inflate(-2, -2), border_radius=max(2, rect.width // 8))


# ---------------------------------------------------------------- the board
def draw_cell(app, surf, cell, rect, col, now, mouse_cell, dt):
    """Draw one cell with all its animations.

    Parameters:
        app (dict): the application state
        surf (pygame.Surface): where to draw
        cell (tuple): (row, col)
        rect (pygame.Rect): place of the cell on the screen
        col (dict): colours of the theme
        now (float): current time
        mouse_cell (tuple): cell under the mouse, or None
        dt (float): time since the last frame

    Returns:
        None
    """
    g = app["game"]
    state = g["state"]
    size = rect.width
    checker = (cell[0] + cell[1]) % 2
    center = rect.center
    target = 1.0 if (cell == mouse_cell and g["end"] is None) else 0.0
    hover = hover_amount(app, ("cell", cell), target, dt)

    revealed = cell in state["revealed"]
    progress = 1.0
    if revealed and cell in g["reveal_anim"]:
        progress = (now - g["reveal_anim"][cell]) / REVEAL_TIME
        if progress >= 1:
            del g["reveal_anim"][cell]
            progress = 1.0

    if not revealed or progress <= 0:
        draw_hidden(surf, rect, col, checker, hover)
    else:
        draw_revealed(surf, rect, col, checker)
        number = state["numbers"][cell[0]][cell[1]]
        if number > 0:
            pop = ease_out_back(progress)
            text_size = max(8, int(size * 0.62 * (0.55 + 0.45 * pop)))
            draw_text(app, surf, str(number), text_size, col["numbers"][number - 1], center, True)
        if progress < 1:
            # the cover of the cell shrinks and fades away
            k = ease_out_cubic(progress)
            cover = pygame.Surface((size, size), pygame.SRCALPHA)
            draw_hidden(cover, pygame.Rect(0, 0, size, size), col, checker, 0)
            new_size = max(1, int(size * (1 - k * 0.85)))
            cover = pygame.transform.smoothscale(cover, (new_size, new_size))
            cover.set_alpha(int(255 * (1 - k)))
            surf.blit(cover, cover.get_rect(center=center))

    # flags (with a spring "pop")
    if cell in state["flags"] or cell in g["flag_anim"]:
        scale = 1.0
        if cell in g["flag_anim"]:
            t = (now - g["flag_anim"][cell]) / FLAG_TIME
            if cell in state["flags"]:
                scale = ease_out_elastic(t)
            else:
                scale = 1 - ease_out_cubic(t * 2.5)
            if t >= 1:
                del g["flag_anim"][cell]
        if cell in state["flags"] or scale > 0.02:
            draw_flag(surf, center, size, scale, col["flag"], col["mine"])

    # mines: debug view, or end of the game
    is_mine = cell in state["mines"]
    if is_mine and not revealed and cell not in state["flags"]:
        if g["end"] is not None and cell in g["mine_anim"]:
            t = (now - g["mine_anim"][cell]) / 0.3
            if t > 0:
                if cell == state["hit_mine"]:
                    pulse = 0.5 + 0.5 * math.sin((now - g["end_time"]) * 9)
                    pygame.draw.rect(surf, lerp_color((200, 0, 0), (255, 60, 60), pulse),
                                     rect.inflate(-2, -2), border_radius=max(2, size // 8))
                if g["end"] == "win":
                    draw_flag(surf, center, size, ease_out_elastic(t), col["flag"], col["mine"])
                else:
                    pop = ease_out_back(t)
                    draw_mine(surf, center, size * pop, col["mine"] if cell != state["hit_mine"] else (20, 0, 0))
        elif g["debug_t"] > 0.01:
            ghost = pygame.Surface((size, size), pygame.SRCALPHA)
            draw_mine(ghost, (size / 2, size / 2), size * 0.9, (200, 30, 30))
            ghost.set_alpha(int(170 * g["debug_t"]))
            surf.blit(ghost, rect)
    # wrong flags at the end of a lost game
    if g["end"] == "lose" and cell in state["flags"] and not is_mine:
        t = (now - g["end_time"] - 0.4) / 0.25
        if t > 0:
            k = ease_out_cubic(t)
            pad = size * 0.22
            red = (220, 30, 30)
            pygame.draw.line(surf, red, (rect.left + pad, rect.top + pad),
                             (lerp(rect.left + pad, rect.right - pad, k), lerp(rect.top + pad, rect.bottom - pad, k)), 3)
            pygame.draw.line(surf, red, (rect.right - pad, rect.top + pad),
                             (lerp(rect.right - pad, rect.left + pad, k), lerp(rect.top + pad, rect.bottom - pad, k)), 3)

    # hint: a ring that pulses for 3 seconds
    if g["hint"] is not None and g["hint"][0] == cell:
        age = now - g["hint"][1]
        if age < 3 and not revealed:
            pulse = 0.5 + 0.5 * math.sin(age * 8)
            ring = rect.inflate(int(4 + 6 * pulse), int(4 + 6 * pulse))
            pygame.draw.rect(surf, col["accent"], ring, 3, border_radius=max(4, size // 5))


def draw_board(app, surf, col, now, dt):
    """Draw the whole board (with the shake after an explosion).

    Parameters:
        app (dict): the application state
        surf (pygame.Surface): where to draw
        col (dict): colours of the theme
        now (float): current time
        dt (float): time since the last frame

    Returns:
        None
    """
    g = app["game"]
    state = g["state"]
    dx = 0
    dy = 0
    if g["shake"] is not None:
        age = now - g["shake"]
        if age < 0.5:
            power = 10 * (1 - age / 0.5)
            dx = math.sin(age * 70) * power
            dy = math.cos(age * 53) * power * 0.6
    size = g["cell"]
    frame = pygame.Rect(g["x0"] - 8 + dx, g["y0"] - 8 + dy, size * state["cols"] + 16, size * state["rows"] + 16)
    if col["style"] == "bevel":
        draw_bevel(surf, frame, col["panel"], col["dark"], col["light"], 4)
    else:
        pygame.draw.rect(surf, lighter(col["bg"], -0.25), frame.move(0, 4), border_radius=14)
        pygame.draw.rect(surf, col["panel"], frame, border_radius=14)
    mouse_cell = cell_at(app, pygame.mouse.get_pos())
    for r in range(state["rows"]):
        for c in range(state["cols"]):
            rect = pygame.Rect(int(g["x0"] + c * size + dx), int(g["y0"] + r * size + dy), size, size)
            draw_cell(app, surf, (r, c), rect, col, now, mouse_cell, dt)
    if g["end"] == "win":
        # a soft green light pulses over the board
        age = now - g["end_time"]
        glow = pygame.Surface((frame.width, frame.height), pygame.SRCALPHA)
        alpha = int(70 * (0.5 + 0.5 * math.sin(age * 4)) * clamp(2.5 - age * 0.5, 0, 1))
        pygame.draw.rect(glow, (120, 255, 140, alpha), glow.get_rect(), border_radius=14)
        surf.blit(glow, frame)


def draw_face(app, surf, center, radius, mood, col, hover):
    """Draw the round face button in the middle of the top bar.

    Parameters:
        app (dict): the application state
        surf (pygame.Surface): where to draw
        center (tuple): (x, y)
        radius (float): size of the face
        mood (str): "normal", "press", "win" or "lose"
        col (dict): colours of the theme
        hover (float): 0 to 1, mouse over the button

    Returns:
        None
    """
    x, y = center
    r = radius * (1 + 0.08 * hover)
    yellow = (255, 214, 10)
    pygame.draw.circle(surf, lighter(yellow, -0.35), (int(x), int(y + 3)), int(r))
    pygame.draw.circle(surf, yellow, (int(x), int(y)), int(r))
    pygame.draw.circle(surf, (60, 40, 0), (int(x), int(y)), int(r), 2)
    eye = r * 0.32
    if mood == "win":
        pygame.draw.rect(surf, (20, 20, 20), (x - r * 0.62, y - r * 0.35, r * 0.55, r * 0.3), border_radius=4)
        pygame.draw.rect(surf, (20, 20, 20), (x + r * 0.07, y - r * 0.35, r * 0.55, r * 0.3), border_radius=4)
        pygame.draw.line(surf, (20, 20, 20), (x - r * 0.1, y - r * 0.25), (x + r * 0.1, y - r * 0.25), 3)
    elif mood == "lose":
        for ex in (-eye, eye):
            pygame.draw.line(surf, (40, 20, 0), (x + ex - 5, y - eye - 5), (x + ex + 5, y - eye + 5), 3)
            pygame.draw.line(surf, (40, 20, 0), (x + ex + 5, y - eye - 5), (x + ex - 5, y - eye + 5), 3)
    else:
        for ex in (-eye, eye):
            pygame.draw.circle(surf, (40, 20, 0), (int(x + ex), int(y - eye * 0.8)), max(2, int(r * 0.11)))
    if mood == "press":
        pygame.draw.circle(surf, (60, 30, 0), (int(x), int(y + r * 0.35)), int(r * 0.18), 3)
    elif mood == "lose":
        pygame.draw.arc(surf, (60, 30, 0), (x - r * 0.45, y + r * 0.25, r * 0.9, r * 0.6), 0.2, math.pi - 0.2, 3)
    else:
        pygame.draw.arc(surf, (60, 30, 0), (x - r * 0.5, y - r * 0.1, r, r * 0.75), math.pi + 0.3, 2 * math.pi - 0.3, 3)


def draw_counter(app, surf, rect, value, icon, col):
    """Draw a counter (mines left or time) with a small icon.

    Parameters:
        app (dict): the application state
        surf (pygame.Surface): where to draw
        rect (pygame.Rect): place of the counter
        value (int): the number to show
        icon (str): "mine" or "clock"
        col (dict): colours of the theme

    Returns:
        None
    """
    if col["style"] == "bevel":
        draw_bevel(surf, rect, col["counter_bg"], col["dark"], col["light"], 2)
    else:
        pygame.draw.rect(surf, col["counter_bg"], rect, border_radius=rect.height // 2)
    icon_center = (rect.left + rect.height * 0.55, rect.centery)
    if icon == "mine":
        draw_mine(surf, icon_center, rect.height * 0.75, col["counter_fg"])
    else:
        pygame.draw.circle(surf, col["counter_fg"], (int(icon_center[0]), int(icon_center[1])), int(rect.height * 0.27), 3)
        pygame.draw.line(surf, col["counter_fg"], icon_center, (icon_center[0], icon_center[1] - rect.height * 0.17), 3)
        pygame.draw.line(surf, col["counter_fg"], icon_center, (icon_center[0] + rect.height * 0.13, icon_center[1]), 3)
    text = str(value)
    if value >= 0:
        text = text.rjust(3, "0")
    draw_text(app, surf, text, int(rect.height * 0.62), col["counter_fg"],
              (rect.right - rect.width * 0.36, rect.centery), True)


def draw_top_bar(app, surf, col, now, dt):
    """Draw the bar with the mines left, the face button and the timer.

    Parameters:
        app (dict): the application state
        surf (pygame.Surface): where to draw
        col (dict): colours of the theme
        now (float): current time
        dt (float): time since the last frame

    Returns:
        None
    """
    g = app["game"]
    state = g["state"]
    bar = pygame.Rect(20, 20, WIDTH - 40, 90)
    if col["style"] == "bevel":
        draw_bevel(surf, bar, col["panel"], col["light"], col["dark"], 3)
    else:
        pygame.draw.rect(surf, lighter(col["bg"], -0.25), bar.move(0, 4), border_radius=18)
        pygame.draw.rect(surf, col["panel"], bar, border_radius=18)
    left = state["nb_mines"] - len(state["flags"])
    draw_counter(app, surf, pygame.Rect(40, 40, 150, 50), left, "mine", col)
    if g["start"] is None:
        seconds = 0
    elif g["end"] is not None:
        seconds = g["seconds"]
    else:
        seconds = int(now - g["start"])
    draw_counter(app, surf, pygame.Rect(WIDTH - 190, 40, 150, 50), min(999, seconds), "clock", col)
    face_rect = pygame.Rect(WIDTH // 2 - 32, 33, 64, 64)
    app["buttons"].append(("restart", face_rect))
    hover = hover_amount(app, "face", 1.0 if face_rect.collidepoint(pygame.mouse.get_pos()) else 0.0, dt)
    mood = "normal"
    if g["end"] == "win":
        mood = "win"
    elif g["end"] == "lose":
        mood = "lose"
    elif g["pressed"]:
        mood = "press"
    bounce = 0
    if g["end_time"] is not None:
        bounce = math.sin(clamp(now - g["end_time"], 0, 0.6) / 0.6 * math.pi) * 6
    draw_face(app, surf, (WIDTH // 2, 65 - bounce), 28, mood, col, hover)


def draw_button(app, surf, key, rect, text, col, dt, main_color):
    """Draw a rounded button that grows a little under the mouse.

    Parameters:
        app (dict): the application state
        surf (pygame.Surface): where to draw
        key (str): name of the button (used for clicks)
        rect (pygame.Rect): place of the button
        text (str): text on the button
        col (dict): colours of the theme
        dt (float): time since the last frame
        main_color (tuple): colour of the button

    Returns:
        None
    """
    app["buttons"].append((key, rect))
    hover = hover_amount(app, key, 1.0 if rect.collidepoint(pygame.mouse.get_pos()) else 0.0, dt)
    grown = rect.inflate(int(8 * hover), int(6 * hover))
    color = lighter(main_color, 0.15 * hover)
    pygame.draw.rect(surf, lighter(main_color, -0.3), grown.move(0, 4), border_radius=grown.height // 2)
    pygame.draw.rect(surf, color, grown, border_radius=grown.height // 2)
    brightness = color[0] * 0.3 + color[1] * 0.59 + color[2] * 0.11
    text_color = (20, 20, 20) if brightness > 150 else (255, 255, 255)
    draw_text(app, surf, text, int(rect.height * 0.45), text_color, grown.center, True)


def draw_overlay(app, surf, col, now, dt):
    """The window at the end of the game, which slides down from the top.

    Parameters:
        app (dict): the application state
        surf (pygame.Surface): where to draw
        col (dict): colours of the theme
        now (float): current time
        dt (float): time since the last frame

    Returns:
        None
    """
    g = app["game"]
    if g["overlay_time"] is None or now < g["overlay_time"]:
        return
    t = ease_out_back((now - g["overlay_time"]) / 0.55)
    shade = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    shade.fill((0, 0, 0, int(110 * clamp((now - g["overlay_time"]) / 0.4, 0, 1))))
    surf.blit(shade, (0, 0))
    w, h = 420, 250
    y = lerp(-h, HEIGHT / 2 - h / 2, t)
    panel = pygame.Rect(WIDTH // 2 - w // 2, int(y), w, h)
    pygame.draw.rect(surf, (0, 0, 0), panel.move(0, 8), border_radius=24)
    pygame.draw.rect(surf, (250, 250, 252), panel, border_radius=24)
    won = g["end"] == "win"
    title = "You won!" if won else "Boom!"
    color = (46, 160, 67) if won else (220, 50, 47)
    draw_text(app, surf, title, 46, color, (panel.centerx, panel.top + 55), True)
    if won:
        line = "Time: " + str(g["seconds"]) + " s"
    else:
        line = "You hit a mine. Try again!"
    draw_text(app, surf, line, 22, (60, 60, 70), (panel.centerx, panel.top + 105), False)
    if g["record"]:
        wobble = math.sin(now * 5) * 0.06
        badge = text_surface(app, "NEW RECORD!", 20, (255, 255, 255), True)
        box = pygame.Surface((badge.get_width() + 24, badge.get_height() + 8), pygame.SRCALPHA)
        pygame.draw.rect(box, (255, 160, 0), box.get_rect(), border_radius=12)
        box.blit(badge, (12, 4))
        box = pygame.transform.rotozoom(box, math.degrees(wobble), 1 + 0.05 * math.sin(now * 7))
        surf.blit(box, box.get_rect(center=(panel.centerx, panel.top + 142)))
    draw_button(app, surf, "again", pygame.Rect(panel.left + 30, panel.bottom - 75, 170, 50), "Play again", col, dt, (46, 125, 220))
    draw_button(app, surf, "menu", pygame.Rect(panel.right - 200, panel.bottom - 75, 170, 50), "Menu", col, dt, (120, 125, 140))


def draw_toast(app, surf, now):
    """Draw the short message at the bottom (it fades after 2 seconds).

    Parameters:
        app (dict): the application state
        surf (pygame.Surface): where to draw
        now (float): current time

    Returns:
        None
    """
    if app["toast"] is None:
        return
    text, start = app["toast"]
    age = now - start
    if age > 2.2:
        app["toast"] = None
        return
    alpha = clamp(min(age / 0.15, (2.2 - age) / 0.4), 0, 1)
    picture = text_surface(app, text, 18, (255, 255, 255), True)
    box = pygame.Surface((picture.get_width() + 30, picture.get_height() + 14), pygame.SRCALPHA)
    pygame.draw.rect(box, (20, 20, 28, 220), box.get_rect(), border_radius=16)
    box.blit(picture, (15, 7))
    box.set_alpha(int(255 * alpha))
    rise = (1 - ease_out_cubic(age / 0.25)) * 20
    surf.blit(box, box.get_rect(center=(WIDTH // 2, HEIGHT - 60 + rise)))


def draw_game(app, surf, now, dt):
    """Draw the whole game screen.

    Parameters:
        app (dict): the application state
        surf (pygame.Surface): where to draw
        now (float): current time
        dt (float): time since the last frame

    Returns:
        None
    """
    col = colors(app, now)
    g = app["game"]
    target = 1.0 if g["debug"] else 0.0
    g["debug_t"] = g["debug_t"] + (target - g["debug_t"]) * clamp(dt * 10, 0, 1)
    surf.fill(col["bg"])
    draw_top_bar(app, surf, col, now, dt)
    draw_board(app, surf, col, now, dt)
    help_text = "Left click: open   Right click: flag   H: hint   D: debug   T: theme   Esc: menu"
    draw_text(app, surf, help_text, 15, lighter(col["text"], -0.1), (WIDTH // 2, HEIGHT - 18), False)
    draw_particles(app, surf)
    draw_overlay(app, surf, col, now, dt)
    draw_toast(app, surf, now)


# ---------------------------------------------------------------- menu
def draw_mini_board(app, surf, rect, theme):
    """A small preview of a theme (4 x 4 cells) in the menu.

    Parameters:
        app (dict): the application state
        surf (pygame.Surface): where to draw
        rect (pygame.Rect): place of the preview
        theme (dict): the theme to show

    Returns:
        None
    """
    size = rect.width // 4
    pattern = ["HH1.", "H21.", "1F1.", "...."]
    for r in range(4):
        for c in range(4):
            cell = pygame.Rect(rect.left + c * size, rect.top + r * size, size, size)
            kind = pattern[r][c]
            if kind == "H" or kind == "F":
                draw_hidden(surf, cell, theme, (r + c) % 2, 0)
                if kind == "F":
                    draw_flag(surf, cell.center, size, 1, theme["flag"], theme["mine"])
            else:
                draw_revealed(surf, cell, theme, (r + c) % 2)
                if kind != ".":
                    n = int(kind)
                    draw_text(app, surf, kind, int(size * 0.6), theme["numbers"][n - 1], cell.center, True)


def draw_menu(app, surf, now, dt):
    """Draw the start screen: levels, safe start, theme, best times.

    Parameters:
        app (dict): the application state
        surf (pygame.Surface): where to draw
        now (float): current time
        dt (float): time since the last frame

    Returns:
        None
    """
    col = colors(app, now)
    surf.fill(col["bg"])
    # small squares floating up in the background
    if len(app["menu_tiles"]) < 26:
        app["menu_tiles"].append({"x": random.uniform(0, WIDTH), "y": HEIGHT + 40,
                                  "s": random.uniform(14, 34), "v": random.uniform(20, 55),
                                  "p": random.uniform(0, 6.28)})
    for tile in app["menu_tiles"]:
        tile["y"] = tile["y"] - tile["v"] * dt
        x = tile["x"] + math.sin(now + tile["p"]) * 12
        square = pygame.Surface((int(tile["s"]), int(tile["s"])), pygame.SRCALPHA)
        pygame.draw.rect(square, col["hidden"] + (60,), square.get_rect(), border_radius=5)
        surf.blit(square, (x, tile["y"]))
    app["menu_tiles"] = [t for t in app["menu_tiles"] if t["y"] > -50]

    # title
    bob = math.sin(now * 2) * 4
    title = draw_text(app, surf, "MINESWEEPER", 52, col["text"], (WIDTH // 2 + 25, 70 + bob), True)
    draw_mine(surf, (title.left - 32, 72 + bob), 52, col["text"])
    draw_text(app, surf, "pygame edition", 18, col["accent"], (WIDTH // 2 + 20, 112 + bob), False)

    # level cards
    names = ["Easy", "Medium", "Hard", "Custom"]
    infos = []
    for level in (1, 2, 3):
        size = LEVELS[level]
        infos.append(str(size[0]) + "x" + str(size[1]) + " - " + str(size[2]))
    infos.append(str(app["custom"][0]) + "x" + str(app["custom"][1]) + " - " + str(app["custom"][2]))
    card_w = 132
    gap = 12
    x_start = (WIDTH - (4 * card_w + 3 * gap)) // 2
    target_x = x_start + (app["level"] - 1) * (card_w + gap)
    if app["sel_x"] == 0:
        app["sel_x"] = target_x
    app["sel_x"] = app["sel_x"] + (target_x - app["sel_x"]) * clamp(dt * 12, 0, 1)
    pygame.draw.rect(surf, col["accent"], (app["sel_x"] - 4, 156, card_w + 8, 98), border_radius=18)
    for i in range(4):
        rect = pygame.Rect(x_start + i * (card_w + gap), 160, card_w, 90)
        app["buttons"].append(("level" + str(i + 1), rect))
        hover = hover_amount(app, "level" + str(i + 1), 1.0 if rect.collidepoint(pygame.mouse.get_pos()) else 0.0, dt)
        pygame.draw.rect(surf, lighter(col["panel"], 0.08 * hover), rect, border_radius=14)
        draw_text(app, surf, names[i], 24, col["panel_text"], (rect.centerx, rect.top + 32), True)
        draw_text(app, surf, infos[i], 16, lighter(col["panel_text"], -0.15), (rect.centerx, rect.top + 62), False)

    y = 280
    # custom size steppers
    if app["level"] == 4:
        labels = ["Rows", "Columns", "Mines"]
        for i in range(3):
            cx = WIDTH // 2 - 190 + i * 190
            draw_text(app, surf, labels[i], 17, col["text"], (cx, y), True)
            draw_button(app, surf, "minus" + str(i), pygame.Rect(cx - 75, y + 18, 40, 40), "-", col, dt, col["hidden"])
            draw_text(app, surf, str(app["custom"][i]), 26, col["text"], (cx, y + 38), True)
            draw_button(app, surf, "plus" + str(i), pygame.Rect(cx + 35, y + 18, 40, 40), "+", col, dt, col["hidden"])
        y = y + 85
    else:
        y = y + 10

    # safe start switch
    switch = pygame.Rect(WIDTH // 2 - 160, y, 320, 50)
    app["buttons"].append(("safe", switch))
    pygame.draw.rect(surf, col["panel"], switch, border_radius=25)
    draw_text(app, surf, "Safe start", 20, col["panel_text"], (switch.left + 95, switch.centery), True)
    track = pygame.Rect(switch.right - 90, switch.top + 12, 60, 26)
    target = 1.0 if app["safe_start"] else 0.0
    app["toggle_x"] = app["toggle_x"] + (target - app["toggle_x"]) * clamp(dt * 14, 0, 1)
    pygame.draw.rect(surf, lerp_color((120, 120, 130), (46, 160, 67), app["toggle_x"]), track, border_radius=13)
    knob_x = lerp(track.left + 13, track.right - 13, app["toggle_x"])
    pygame.draw.circle(surf, (255, 255, 255), (int(knob_x), track.centery), 11)

    # theme selector with a preview
    y = y + 75
    box = pygame.Rect(WIDTH // 2 - 200, y, 400, 120)
    pygame.draw.rect(surf, col["panel"], box, border_radius=18)
    draw_button(app, surf, "theme_prev", pygame.Rect(box.left + 15, box.centery - 22, 44, 44), "<", col, dt, col["hidden"])
    draw_button(app, surf, "theme_next", pygame.Rect(box.right - 59, box.centery - 22, 44, 44), ">", col, dt, col["hidden"])
    draw_text(app, surf, "Theme", 16, lighter(col["panel_text"], -0.15), (box.centerx - 55, box.top + 35), False)
    draw_text(app, surf, THEMES[app["theme"]]["name"], 30, col["panel_text"], (box.centerx - 55, box.top + 70), True)
    draw_mini_board(app, surf, pygame.Rect(box.right - 170, box.top + 12, 96, 96), THEMES[app["theme"]])

    # best times
    y = y + 140
    draw_text(app, surf, "Best times", 20, col["text"], (WIDTH // 2, y), True)
    keys = list(app["scores"].keys())
    if len(keys) == 0:
        draw_text(app, surf, "no game won yet", 16, lighter(col["text"], -0.2), (WIDTH // 2, y + 28), False)
    for i in range(min(3, len(keys))):
        line = keys[i] + ":  " + str(app["scores"][keys[i]]) + " s"
        draw_text(app, surf, line, 16, lighter(col["text"], -0.1), (WIDTH // 2, y + 28 + i * 22), False)

    # start button with a soft pulse
    pulse = 0.5 + 0.5 * math.sin(now * 3)
    start = pygame.Rect(WIDTH // 2 - 120, HEIGHT - 120, 240, 64)
    glow = pygame.Surface((start.width + 40, start.height + 40), pygame.SRCALPHA)
    pygame.draw.rect(glow, (46, 160, 67, int(40 + 50 * pulse)), glow.get_rect(), border_radius=40)
    surf.blit(glow, (start.left - 20, start.top - 20))
    draw_button(app, surf, "start", start, "START", col, dt, (46, 160, 67))
    draw_text(app, surf, "Enter: start   1-4: level   T: theme   Esc: quit", 15,
              lighter(col["text"], -0.15), (WIDTH // 2, HEIGHT - 25), False)


# ---------------------------------------------------------------- events
def menu_click(app, key, now):
    """What to do when a button of the menu is clicked.

    Parameters:
        app (dict): the application state
        key (str): name of the button
        now (float): current time

    Returns:
        None
    """
    if key.startswith("level"):
        app["level"] = int(key[5])
    elif key == "safe":
        app["safe_start"] = not app["safe_start"]
    elif key == "theme_next":
        change_theme(app, now)
    elif key == "theme_prev":
        app["old_theme"] = app["theme"]
        app["theme"] = (app["theme"] - 1) % len(THEMES)
        app["theme_time"] = now
    elif key == "start":
        start_game(app, now)
    elif key.startswith("plus") or key.startswith("minus"):
        i = int(key[-1])
        step = 1 if key.startswith("plus") else -1
        values = app["custom"]
        values[i] = values[i] + step
        values[0] = int(clamp(values[0], 5, 20))
        values[1] = int(clamp(values[1], 5, 20))
        values[2] = int(clamp(values[2], 1, values[0] * values[1] // 4))


def button_under(app, pos):
    """Name of the button under the mouse (buttons of the last frame).

    Parameters:
        app (dict): the application state
        pos (tuple): (x, y) of the mouse

    Returns:
        str: the name of the button, or None
    """
    found = None
    for key, rect in app["buttons"]:
        if rect.collidepoint(pos):
            found = key
    return found


def handle_event(app, event, now):
    """React to one event (mouse or keyboard).

    Parameters:
        app (dict): the application state
        event (pygame.event.Event): the event
        now (float): current time

    Returns:
        bool: False to close the program, otherwise True
    """
    if event.type == pygame.QUIT:
        return False
    if app["mode"] == "menu":
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            key = button_under(app, event.pos)
            if key is not None:
                menu_click(app, key, now)
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return False
            if event.key == pygame.K_RETURN:
                start_game(app, now)
            if event.key == pygame.K_t:
                change_theme(app, now)
            if event.key in (pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4):
                app["level"] = event.key - pygame.K_0
        return True

    g = app["game"]
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_ESCAPE:
            app["mode"] = "menu"
        elif event.key == pygame.K_t:
            change_theme(app, now)
        elif event.key == pygame.K_r:
            start_game(app, now)
        elif event.key == pygame.K_d and g["end"] is None:
            if g["state"]["first_move"]:
                show_toast(app, "No mines yet: they are placed after your first reveal.", now)
            else:
                g["debug"] = not g["debug"]
        elif event.key == pygame.K_h and g["end"] is None:
            use_hint(app, now)
        return True
    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        g["pressed"] = True
    if event.type == pygame.MOUSEBUTTONUP:
        g["pressed"] = False
        key = button_under(app, event.pos)
        if key == "restart" or key == "again":
            start_game(app, now)
            return True
        if key == "menu":
            app["mode"] = "menu"
            return True
        if g["end"] is not None:
            return True
        cell = cell_at(app, event.pos)
        if cell is None:
            return True
        if event.button == 1:
            click_reveal(app, cell, now)
        elif event.button == 3:
            click_flag(app, cell, now)
    return True


# ---------------------------------------------------------------- main loop
def run_frame(app, now, dt):
    """Update and draw one picture of the window.

    Parameters:
        app (dict): the application state
        now (float): current time
        dt (float): time since the last frame

    Returns:
        None
    """
    app["buttons"] = []
    update_particles(app, dt)
    if app["mode"] == "menu":
        draw_menu(app, app["screen"], now, dt)
    else:
        draw_game(app, app["screen"], now, dt)


def main():
    """Open the window and run the game until it is closed.

    Returns:
        None
    """
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Minesweeper - pygame edition")
    clock = pygame.time.Clock()
    app = new_app(screen)
    running = True
    while running:
        dt = clock.tick(FPS) / 1000
        now = time.time()
        for event in pygame.event.get():
            if handle_event(app, event, now) == False:
                running = False
        run_frame(app, now, dt)
        pygame.display.flip()
    pygame.quit()


if __name__ == "__main__":
    main()
