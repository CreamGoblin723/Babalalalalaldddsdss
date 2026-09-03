"""Procedural pixel-art generation.

Every visual in the game is built at runtime from tiny character-grid
"pixel maps" scaled up with nearest-neighbour scaling. This keeps the game
fully self-contained (no external art assets to ship or fetch) while still
giving it a chunky, deliberate pixel-art look.
"""
import pygame

from game.ui import get_font

_CACHE = {}


def _grid_to_surface(rows, palette, pixel_size=1):
    """rows: list[str] of equal length, each char is a palette key or '.'
    for transparent. Returns a pygame.Surface with per-pixel alpha."""
    h = len(rows)
    w = len(rows[0]) if h else 0
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            if ch == "." or ch not in palette:
                continue
            surf.set_at((x, y), palette[ch])
    if pixel_size != 1:
        surf = pygame.transform.scale(surf, (w * pixel_size, h * pixel_size))
    return surf


def _cached(key, builder):
    if key not in _CACHE:
        _CACHE[key] = builder()
    return _CACHE[key]


# ---------------------------------------------------------------------------
# Characters
# ---------------------------------------------------------------------------
SKIN_PALETTES = {
    "drifter": {"outfit": (92, 92, 100), "outfit2": (64, 64, 72), "trim": (176, 176, 184)},
    "red_suit": {"outfit": (168, 26, 34), "outfit2": (110, 16, 22), "trim": (232, 181, 74)},
    "purple_hood": {"outfit": (86, 52, 122), "outfit2": (54, 30, 82), "trim": (200, 170, 230)},
    "gold_baron": {"outfit": (232, 181, 74), "outfit2": (156, 116, 42), "trim": (255, 250, 230)},
    "neon_ghost": {"outfit": (68, 214, 122), "outfit2": (24, 120, 70), "trim": (220, 255, 240)},
}

SKIN_ORDER = ["drifter", "red_suit", "purple_hood", "gold_baron", "neon_ghost"]
SKIN_NAMES = {
    "drifter": "The Drifter",
    "red_suit": "Red Suit",
    "purple_hood": "Purple Hood",
    "gold_baron": "Gold Baron",
    "neon_ghost": "Neon Ghost",
}
SKIN_COSTS = {
    "drifter": 0,
    "red_suit": 40,
    "purple_hood": 90,
    "gold_baron": 180,
    "neon_ghost": 320,
}

_SKIN_HEAD = (222, 176, 140)


def _build_walk_frame(step_offset, skin):
    pal = SKIN_PALETTES[skin]
    o, o2, tr = pal["outfit"], pal["outfit2"], pal["trim"]
    palette = {
        "H": _SKIN_HEAD,
        "T": o,
        "S": o2,
        "R": tr,
        "1": o2,
        "2": (40, 34, 30),
    }
    if step_offset == 0:
        rows = [
            "..HHHH..",
            ".HHHHHH.",
            ".HHHHHH.",
            "..HHHH..",
            ".TTTTTT.",
            "TTTRRTTT",
            "TT.TT.TT",
            "1S.TT.S1",
            "..2..2..",
            "........",
        ]
    else:
        rows = [
            "..HHHH..",
            ".HHHHHH.",
            ".HHHHHH.",
            "..HHHH..",
            ".TTTTTT.",
            "TTTRRTTT",
            "TTS..STT",
            "TT.11.TT",
            ".2....2.",
            "........",
        ]
    return _grid_to_surface(rows, palette)


def get_character_sprite(skin: str, direction: str = "down", frame: int = 0, pixel_size: int = 3):
    if skin not in SKIN_PALETTES:
        skin = "drifter"
    key = ("char", skin, direction, frame, pixel_size)

    def build():
        base = _build_walk_frame(frame % 2, skin)
        # Facing left/right is just a horizontal flip; up/down share art
        # (top-down games rarely show a real back/front distinction at
        # this pixel density, so we tint "up" slightly darker instead).
        if direction == "left":
            base = pygame.transform.flip(base, True, False)
        elif direction == "up":
            tinted = base.copy()
            dark = pygame.Surface(tinted.get_size(), pygame.SRCALPHA)
            dark.fill((0, 0, 0, 70))
            tinted.blit(dark, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            base = tinted
        return pygame.transform.scale(
            base, (base.get_width() * pixel_size, base.get_height() * pixel_size)
        )

    return _cached(key, build)


def get_shady_man_sprite(pixel_size: int = 3):
    key = ("shady_man", pixel_size)

    def build():
        palette = {
            "H": (60, 54, 66),   # wide-brim hat
            "S": (40, 20, 24),   # shadowed face
            "E": (214, 46, 46),  # glowing eyes
            "T": (30, 26, 38),   # trench coat
            "R": (232, 181, 74),
        }
        rows = [
            ".HHHHHHHH.",
            "HHHHHHHHHH",
            ".SSSSSSSS.",
            ".SE.SS.ES.",
            "..SSSSSS..",
            ".TTTTTTTT.",
            ".TTTTTTTT.",
            ".TTTRRTTT.",
            ".TT.TT.TT.",
            ".T.....T.",
        ]
        # fix row width consistency
        rows = [r.ljust(10, ".")[:10] for r in rows]
        pal = {
            "H": palette["H"], "S": palette["S"], "E": palette["E"],
            "T": palette["T"], "R": palette["R"],
        }
        surf = _grid_to_surface(rows, pal)
        return pygame.transform.scale(surf, (surf.get_width() * pixel_size, surf.get_height() * pixel_size))

    return _cached(key, build)


# ---------------------------------------------------------------------------
# Environment props
# ---------------------------------------------------------------------------
def get_van_sprite(pixel_size: int = 3):
    key = ("van", pixel_size)

    def build():
        palette = {
            "B": (58, 36, 26),
            "b": (78, 50, 34),
            "W": (24, 24, 28),
            "G": (140, 200, 220),
            "R": (168, 26, 34),
            "L": (232, 181, 74),
        }
        rows = [
            "..bbbbbbbbbbbb..",
            ".bBBBBBBBBBBBBb.",
            "bBBBGGGGGGGGGBBb",
            "bBBBGGGGGGGGGBBb",
            "bBBBBBBBBBBBBBBb",
            "bBBRRRRRRRRRBBBb",
            "bBBBBBBBBBBBBBBb",
            "WWbBBBBBBBBBBbWW",
            ".WW..LLLL..WW..",
        ]
        rows = [r.ljust(16, ".")[:16] for r in rows]
        surf = _grid_to_surface(rows, palette)
        return pygame.transform.scale(surf, (surf.get_width() * pixel_size, surf.get_height() * pixel_size))

    return _cached(key, build)


def get_casino_facade(width_tiles=12, height_tiles=7, pixel_size=3):
    key = ("casino_facade", width_tiles, height_tiles, pixel_size)

    def build():
        w, h = width_tiles * 8, height_tiles * 8
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        surf.fill((44, 26, 66))
        # base wall
        pygame.draw.rect(surf, (58, 36, 26), (0, 0, w, h))
        pygame.draw.rect(surf, (30, 18, 14), (0, 0, w, h), 3)
        # neon sign band
        pygame.draw.rect(surf, (168, 26, 34), (4, 4, w - 8, 16))
        pygame.draw.rect(surf, (232, 181, 74), (4, 4, w - 8, 16), 2)
        # door
        door_w = 24
        pygame.draw.rect(surf, (20, 18, 24), (w // 2 - door_w // 2, h - 30, door_w, 30))
        pygame.draw.rect(surf, (232, 181, 74), (w // 2 - door_w // 2, h - 30, door_w, 30), 2)
        # windows with warm glow
        for wx in range(16, w - 16, 28):
            if wx + 12 > w // 2 - door_w // 2 - 6 and wx < w // 2 + door_w // 2 + 6:
                continue
            pygame.draw.rect(surf, (232, 181, 74), (wx, h - 44, 12, 12))
            pygame.draw.rect(surf, (120, 20, 24), (wx, h - 44, 12, 12), 1)
        return pygame.transform.scale(surf, (w * pixel_size, h * pixel_size))

    return _cached(key, build)


def get_table_sprite(kind="blackjack", pixel_size=3):
    key = ("table", kind, pixel_size)

    def build():
        w, h = 32, 20
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        if kind == "slots":
            return _build_slot_machine_icon(w, h, pixel_size)
        if kind == "roulette":
            return _build_roulette_icon(w, h, pixel_size)
        felt = {
            "blackjack": (24, 92, 60),
            "coinflip": (46, 66, 122),
            "overunder": (122, 46, 66),
        }.get(kind, (24, 92, 60))
        pygame.draw.ellipse(surf, (58, 36, 26), (0, 4, w, h - 4))
        pygame.draw.ellipse(surf, felt, (2, 5, w - 4, h - 7))
        pygame.draw.ellipse(surf, (232, 181, 74), (2, 5, w - 4, h - 7), 1)
        # a subtle felt highlight band gives the table a bit of shading depth
        pygame.draw.arc(surf, (255, 255, 255, 60), (3, 6, w - 6, h - 9), 3.6, 5.6, 1)
        return pygame.transform.scale(surf, (w * pixel_size, h * pixel_size))

    return _cached(key, build)


def _build_slot_machine_icon(w, h, pixel_size):
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    body = pygame.Rect(w // 2 - 9, 2, 18, h - 3)
    pygame.draw.rect(surf, (168, 26, 34), body, border_radius=2)
    pygame.draw.rect(surf, (232, 181, 74), body, 1, border_radius=2)
    screen = pygame.Rect(body.x + 2, body.y + 2, body.w - 4, 7)
    pygame.draw.rect(surf, (20, 18, 24), screen)
    for i, col in enumerate(((214, 46, 46), (232, 181, 74), (68, 214, 122))):
        pygame.draw.rect(surf, col, (screen.x + 1 + i * 4, screen.y + 1, 3, screen.h - 2))
    pygame.draw.circle(surf, (232, 181, 74), (body.right + 1, body.y + 5), 2)
    return pygame.transform.scale(surf, (w * pixel_size, h * pixel_size))


def _build_roulette_icon(w, h, pixel_size):
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    cx, cy, r = w // 2, h // 2 + 1, min(w, h) // 2 - 1
    pygame.draw.circle(surf, (58, 36, 26), (cx, cy), r + 1)
    for i in range(10):
        color = (168, 26, 34) if i % 2 == 0 else (20, 20, 24)
        start = i / 10 * 6.283
        end = (i + 1) / 10 * 6.283
        pygame.draw.arc(surf, color, (cx - r, cy - r, r * 2, r * 2), start, end, r)
    pygame.draw.circle(surf, (232, 181, 74), (cx, cy), r, 1)
    pygame.draw.circle(surf, (240, 240, 235), (cx, cy), 2)
    return pygame.transform.scale(surf, (w * pixel_size, h * pixel_size))


def get_floor_tile(kind="wood", pixel_size=3, size=16):
    key = ("floor", kind, pixel_size, size)

    def build():
        surf = pygame.Surface((size, size))
        if kind == "wood":
            surf.fill((92, 58, 40))
            for i in range(0, size, 4):
                pygame.draw.line(surf, (78, 48, 32), (0, i), (size, i))
        elif kind == "grass":
            surf.fill((28, 74, 44))
            for i in range(0, size, 5):
                pygame.draw.line(surf, (22, 62, 36), (i, 0), (i, size))
        elif kind == "asphalt":
            surf.fill((46, 46, 54))
            for i in range(0, size, 6):
                for j in range(0, size, 6):
                    if (i + j) % 12 == 0:
                        surf.set_at((i, j), (56, 56, 64))
        elif kind == "carpet":
            surf.fill((120, 20, 24))
            pygame.draw.rect(surf, (94, 14, 18), (2, 2, size - 4, size - 4), 1)
        else:
            surf.fill((60, 60, 60))
        return pygame.transform.scale(surf, (size * pixel_size, size * pixel_size))

    return _cached(key, build)


def get_chip_icon(radius=6, color=(232, 181, 74)):
    key = ("chip", radius, color)

    def build():
        d = radius * 2 + 2
        surf = pygame.Surface((d, d), pygame.SRCALPHA)
        pygame.draw.circle(surf, color, (d // 2, d // 2), radius)
        pygame.draw.circle(surf, (20, 20, 24), (d // 2, d // 2), radius, 2)
        pygame.draw.circle(surf, (255, 255, 255, 90), (d // 2, d // 2), radius - 3, 1)
        return surf

    return _cached(key, build)


def get_playing_card(rank=None, suit=None, face_down=False, width=40, height=56):
    """rank in ('A',2..10,'J','Q','K'); suit in ('S','H','D','C')."""
    key = ("card", rank, suit, face_down, width, height)

    def build():
        surf = pygame.Surface((width, height), pygame.SRCALPHA)
        if face_down:
            pygame.draw.rect(surf, (86, 52, 122), (0, 0, width, height), border_radius=4)
            pygame.draw.rect(surf, (232, 181, 74), (0, 0, width, height), 2, border_radius=4)
            pygame.draw.rect(surf, (54, 30, 82), (5, 5, width - 10, height - 10), border_radius=3)
            return surf
        pygame.draw.rect(surf, (240, 240, 235), (0, 0, width, height), border_radius=4)
        pygame.draw.rect(surf, (20, 20, 24), (0, 0, width, height), 2, border_radius=4)
        red = suit in ("H", "D")
        color = (168, 26, 34) if red else (20, 20, 24)
        font = pygame.font.SysFont("dejavusansmono", 14, bold=True)
        label = font.render(str(rank), True, color)
        surf.blit(label, (4, 3))
        suit_glyph = {"S": "♠", "H": "♥", "D": "♦", "C": "♣"}.get(suit, "?")
        try:
            sfont = pygame.font.SysFont("dejavusansmono", 18, bold=True)
            sglyph = sfont.render(suit_glyph, True, color)
        except Exception:
            sglyph = font.render(suit_glyph, True, color)
        surf.blit(sglyph, (width // 2 - sglyph.get_width() // 2, height // 2 - sglyph.get_height() // 2))
        label2 = font.render(str(rank), True, color)
        label2 = pygame.transform.rotate(label2, 180)
        surf.blit(label2, (width - label2.get_width() - 4, height - label2.get_height() - 3))
        return surf

    return _cached(key, build)


def get_coin_sprite(face="heads", radius=24):
    key = ("coin", face, radius)

    def build():
        d = radius * 2
        surf = pygame.Surface((d, d), pygame.SRCALPHA)
        color = (232, 181, 74) if face == "heads" else (196, 150, 60)
        pygame.draw.circle(surf, color, (d // 2, d // 2), radius)
        pygame.draw.circle(surf, (120, 90, 30), (d // 2, d // 2), radius, 3)
        font = pygame.font.SysFont("dejavusansmono", int(radius * 0.9), bold=True)
        glyph = "H" if face == "heads" else "T"
        label = font.render(glyph, True, (60, 40, 10))
        surf.blit(label, (d // 2 - label.get_width() // 2, d // 2 - label.get_height() // 2))
        return surf

    return _cached(key, build)


def get_die_face(value: int, size=40):
    key = ("die", value, size)

    def build():
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.rect(surf, (240, 240, 235), (0, 0, size, size), border_radius=6)
        pygame.draw.rect(surf, (20, 20, 24), (0, 0, size, size), 2, border_radius=6)
        pip = (20, 20, 24)
        r = max(2, size // 12)
        cx, cy = size // 2, size // 2
        q = size // 4
        positions = {
            1: [(cx, cy)],
            2: [(cx - q, cy - q), (cx + q, cy + q)],
            3: [(cx - q, cy - q), (cx, cy), (cx + q, cy + q)],
            4: [(cx - q, cy - q), (cx + q, cy - q), (cx - q, cy + q), (cx + q, cy + q)],
            5: [(cx - q, cy - q), (cx + q, cy - q), (cx, cy), (cx - q, cy + q), (cx + q, cy + q)],
            6: [(cx - q, cy - q), (cx + q, cy - q), (cx - q, cy), (cx + q, cy),
                (cx - q, cy + q), (cx + q, cy + q)],
        }
        for (px, py) in positions.get(value, []):
            pygame.draw.circle(surf, pip, (px, py), r)
        return surf

    return _cached(key, build)


# ---------------------------------------------------------------------------
# Slots & Roulette
# ---------------------------------------------------------------------------
def get_slot_symbol(name: str, size=40):
    key = ("slot_symbol", name, size)

    def build():
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.rect(surf, (18, 16, 22), (0, 0, size, size), border_radius=4)
        pygame.draw.rect(surf, (70, 64, 78), (0, 0, size, size), 1, border_radius=4)
        cx, cy = size // 2, size // 2
        if name == "cherry":
            r = max(3, size // 7)
            pygame.draw.line(surf, (70, 140, 60), (cx, cy - r), (cx + 2, cy - r * 3), 2)
            pygame.draw.circle(surf, (206, 30, 46), (cx - r, cy + r), r)
            pygame.draw.circle(surf, (206, 30, 46), (cx + r, cy + r), r)
            pygame.draw.circle(surf, (255, 255, 255, 80), (cx - r - 1, cy + r - 1), max(1, r // 3))
        elif name == "bell":
            gold = (232, 181, 74)
            pygame.draw.polygon(surf, gold, [
                (cx, cy - size // 3), (cx - size // 3, cy + size // 6),
                (cx + size // 3, cy + size // 6),
            ])
            pygame.draw.rect(surf, gold, (cx - size // 3, cy + size // 6, size * 2 // 3, size // 8))
            pygame.draw.circle(surf, (156, 116, 42), (cx, cy + size // 6 + size // 8 + 2), size // 12)
        elif name == "bar":
            pygame.draw.rect(surf, (20, 20, 24), (4, cy - size // 6, size - 8, size // 3), border_radius=2)
            pygame.draw.rect(surf, (232, 181, 74), (4, cy - size // 6, size - 8, size // 3), 1, border_radius=2)
            font = get_font(max(8, size // 4), bold=True)
            label = font.render("BAR", True, (232, 181, 74))
            surf.blit(label, label.get_rect(center=(cx, cy)))
        elif name == "chip":
            chip = get_chip_icon(radius=size // 2 - 4)
            surf.blit(chip, chip.get_rect(center=(cx, cy)))
        elif name == "seven":
            font = get_font(int(size * 0.6), bold=True)
            label = font.render("7", True, (232, 181, 74))
            surf.blit(label, label.get_rect(center=(cx, cy)))
        return surf

    return _cached(key, build)


def get_slot_machine_sprite(pixel_size=3):
    key = ("slot_machine", pixel_size)

    def build():
        w, h = 46, 60
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        cabinet = pygame.Rect(3, 6, w - 6, h - 12)
        pygame.draw.rect(surf, (168, 26, 34), cabinet, border_radius=4)
        pygame.draw.rect(surf, (232, 181, 74), cabinet, 2, border_radius=4)
        marquee = pygame.Rect(cabinet.x + 2, cabinet.y + 2, cabinet.w - 4, 10)
        pygame.draw.rect(surf, (20, 18, 24), marquee, border_radius=2)
        font = get_font(7, bold=True)
        label = font.render("LUCKY 7s", True, (232, 181, 74))
        surf.blit(label, label.get_rect(center=marquee.center))
        window = pygame.Rect(cabinet.x + 4, marquee.bottom + 3, cabinet.w - 8, 18)
        pygame.draw.rect(surf, (240, 240, 235), window)
        pygame.draw.rect(surf, (20, 20, 24), window, 1)
        for i in range(3):
            pygame.draw.line(surf, (200, 200, 195), (window.x + (i + 1) * window.w // 3, window.y),
                              (window.x + (i + 1) * window.w // 3, window.bottom))
        lever_x = cabinet.right + 1
        pygame.draw.line(surf, (60, 60, 68), (lever_x, cabinet.y + 6), (lever_x, cabinet.y + 20), 2)
        pygame.draw.circle(surf, (214, 46, 46), (lever_x, cabinet.y + 4), 3)
        pygame.draw.rect(surf, (58, 36, 26), (6, cabinet.bottom, w - 12, 4))
        return pygame.transform.scale(surf, (w * pixel_size, h * pixel_size))

    return _cached(key, build)


def get_roulette_wheel_sprite(size=90, wedges=12):
    key = ("roulette_wheel", size, wedges)

    def build():
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        cx = cy = size // 2
        r = size // 2 - 2
        pygame.draw.circle(surf, (58, 36, 26), (cx, cy), r + 3)
        for i in range(wedges):
            if i == 0:
                color = (68, 214, 122)
            elif i % 2 == 0:
                color = (168, 26, 34)
            else:
                color = (18, 18, 22)
            start = i / wedges * 6.28318
            end = (i + 1) / wedges * 6.28318
            pygame.draw.arc(surf, color, (cx - r, cy - r, r * 2, r * 2), start, end, max(3, r // 3))
        pygame.draw.circle(surf, (232, 181, 74), (cx, cy), r, 2)
        pygame.draw.circle(surf, (30, 26, 20), (cx, cy), max(4, r // 4))
        pygame.draw.circle(surf, (232, 181, 74), (cx, cy), max(4, r // 4), 1)
        return surf

    return _cached(key, build)


def get_number_badge(number: int, color_name: str, size=30):
    key = ("number_badge", number, color_name, size)

    def build():
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        fill = {"red": (168, 26, 34), "black": (20, 20, 24), "green": (24, 130, 76)}.get(color_name, (80, 80, 80))
        cx = cy = size // 2
        pygame.draw.circle(surf, fill, (cx, cy), size // 2 - 1)
        pygame.draw.circle(surf, (232, 181, 74), (cx, cy), size // 2 - 1, 2)
        font = get_font(int(size * 0.4), bold=True)
        label = font.render(str(number), True, (245, 245, 240))
        surf.blit(label, label.get_rect(center=(cx, cy)))
        return surf

    return _cached(key, build)


# ---------------------------------------------------------------------------
# The Bar
# ---------------------------------------------------------------------------
def get_bar_counter_sprite(pixel_size=3):
    key = ("bar_counter", pixel_size)

    def build():
        w, h = 64, 48
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(surf, (58, 36, 26), (0, 0, w, h - 10))
        pygame.draw.rect(surf, (30, 18, 14), (0, 0, w, h - 10), 3)
        for shelf_y in (6, 16):
            pygame.draw.rect(surf, (40, 24, 18), (4, shelf_y, w - 8, 3))
            bottle_colors = [(168, 26, 34), (68, 214, 122), (232, 181, 74), (86, 52, 122), (46, 66, 122)]
            for i, bx in enumerate(range(8, w - 8, 8)):
                color = bottle_colors[i % len(bottle_colors)]
                pygame.draw.rect(surf, color, (bx, shelf_y - 8, 3, 8))
        pygame.draw.rect(surf, (92, 58, 40), (0, h - 14, w, 14), border_radius=2)
        pygame.draw.rect(surf, (232, 181, 74), (0, h - 14, w, 14), 1, border_radius=2)
        return pygame.transform.scale(surf, (w * pixel_size, h * pixel_size))

    return _cached(key, build)


def get_bartender_sprite(pixel_size=3):
    key = ("bartender", pixel_size)

    def build():
        palette = {
            "H": _SKIN_HEAD,
            "M": (60, 44, 30),    # slicked hair / mustache
            "A": (240, 240, 235),  # apron
            "S": (64, 64, 72),    # shirt/vest
        }
        rows = [
            "..HHHH..",
            ".HHHHHH.",
            ".HMHHHM.",
            "..HHHH..",
            ".SSSSSS.",
            "SSAAAASS",
            "SS.AA.SS",
            "SS.AA.SS",
            "..2..2..",
            "........",
        ]
        rows = [r.ljust(8, ".")[:8] for r in rows]
        pal = dict(palette)
        pal["2"] = (40, 34, 30)
        surf = _grid_to_surface(rows, pal)
        return pygame.transform.scale(surf, (surf.get_width() * pixel_size, surf.get_height() * pixel_size))

    return _cached(key, build)
