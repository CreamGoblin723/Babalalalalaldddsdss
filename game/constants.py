"""Global constants shared across the game."""
import os

# --- Window / rendering -----------------------------------------------
SCREEN_WIDTH = 960
SCREEN_HEIGHT = 640
FPS = 60
TITLE = "BLOOD & CHIPS"

# The whole game is drawn at a low internal resolution and then scaled
# up with no smoothing, which is what gives everything its chunky
# pixel-art look without needing any external art assets. GameApp letterboxes
# this to fit any real window/fullscreen size while keeping this aspect
# ratio exact, so the actual on-screen scale factor is computed at runtime
# rather than fixed here.
INTERNAL_WIDTH = 320
INTERNAL_HEIGHT = 213

TILE_SIZE = 16

# --- Paths ---------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAVES_DIR = os.path.join(BASE_DIR, "saves")
META_SAVE_PATH = os.path.join(SAVES_DIR, "meta.json")
SETTINGS_PATH = os.path.join(SAVES_DIR, "settings.json")
SAVE_SLOT_TEMPLATE = os.path.join(SAVES_DIR, "slot_{}.json")
NUM_SAVE_SLOTS = 3

# --- Palette (pixel-art restricted palette) -------------------------------
BLACK = (10, 10, 14)
WHITE = (240, 240, 235)
DARK_RED = (120, 20, 24)
BLOOD_RED = (168, 26, 34)
BRIGHT_RED = (214, 46, 46)
GOLD = (232, 181, 74)
DARK_GOLD = (156, 116, 42)
GREEN_FELT = (24, 92, 60)
DARK_GREEN = (14, 56, 38)
NEON_GREEN = (68, 214, 122)
PURPLE = (86, 52, 122)
DARK_PURPLE = (44, 26, 66)
BROWN = (92, 58, 40)
DARK_BROWN = (58, 36, 26)
SKY_NIGHT = (24, 22, 46)
ASPHALT = (46, 46, 54)
ASPHALT_DARK = (30, 30, 36)
GREY = (120, 120, 128)
LIGHT_GREY = (176, 176, 184)
SAND = (196, 168, 110)
WOOD = (120, 78, 48)

UI_BG = (18, 16, 24)
UI_PANEL = (30, 26, 38)
UI_BORDER = GOLD
UI_TEXT = WHITE
UI_TEXT_DIM = (150, 148, 158)
UI_ACCENT = BLOOD_RED
UI_SELECT = NEON_GREEN

# --- Gameplay --------------------------------------------------------------
WIN_CHIPS = 1_000_000
STARTING_CHIPS = 500
PLAYER_SPEED = 90  # pixels/second at internal resolution

# Blood Money conversion: how much Blood Money a run is worth when it ends,
# based on the peak amount of chips that were ever held during that run.
def blood_money_from_peak(peak_chips: int) -> int:
    if peak_chips <= STARTING_CHIPS:
        return 1
    import math
    # Diminishing logarithmic curve so early runs still feel rewarding but
    # the grind to 1,000,000 chips isn't trivially bypassed by Blood Money.
    return max(1, int(math.log2(max(2, peak_chips / STARTING_CHIPS)) * 12))


DIRECTIONS = {
    "up": (0, -1),
    "down": (0, 1),
    "left": (-1, 0),
    "right": (1, 0),
}
