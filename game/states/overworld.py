import pygame

from game import constants as C
from game.states.topdown import TopDownState
from game.ui import draw_text
from game.sprites import get_van_sprite, get_casino_facade, get_shady_man_sprite, get_floor_tile


def _rect(x, y, w, h):
    return pygame.Rect(x, y, w, h)


MAPS = {
    "home": {
        "floor": "grass",
        "bounds": _rect(8, 8, C.INTERNAL_WIDTH - 16, C.INTERNAL_HEIGHT - 16),
        "obstacles": [
            _rect(20, 20, 60, 30),   # a shack
            _rect(C.INTERNAL_WIDTH - 80, 20, 60, 24),
        ],
        "van": _rect(C.INTERNAL_WIDTH // 2 - 24, C.INTERNAL_HEIGHT - 60, 48, 32),
        "spawn": (C.INTERNAL_WIDTH // 2, C.INTERNAL_HEIGHT // 2 + 30),
        "label": "Home Lot",
    },
    "casino_area": {
        "floor": "asphalt",
        "bounds": _rect(8, 8, C.INTERNAL_WIDTH - 16, C.INTERNAL_HEIGHT - 16),
        "obstacles": [
            _rect(C.INTERNAL_WIDTH // 2 - 60, 20, 120, 60),  # casino building footprint
        ],
        "casino_door": _rect(C.INTERNAL_WIDTH // 2 - 14, 68, 28, 12),
        "shady_man": _rect(C.INTERNAL_WIDTH // 2 + 70, 40, 16, 16),
        "van": _rect(20, C.INTERNAL_HEIGHT - 50, 44, 30),
        "spawn": (40, C.INTERNAL_HEIGHT - 70),
        "label": "The Strip",
    },
}


class OverworldState(TopDownState):
    def on_enter(self, map_name="home", spawn=None, **kwargs):
        self._load_map(map_name, spawn)

    def on_resume(self, **kwargs):
        pass  # returning from casino interior / shop; player position unchanged

    def _load_map(self, map_name, spawn=None):
        self.map_name = map_name
        self.map = MAPS[map_name]
        self.bounds = self.map["bounds"]
        self.obstacles = self.map.get("obstacles", [])
        player = self.app.player
        player.map_name = map_name
        if spawn is not None:
            player.x, player.y = spawn
        self.prompt = None
        self.floor_tile = get_floor_tile(self.map["floor"], pixel_size=1, size=16)

    def interact_zones(self):
        zones = {}
        for key in ("van", "casino_door", "shady_man"):
            if key in self.map:
                zones[key] = self.map[key]
        return zones

    def on_interact(self, name):
        if name == "van":
            self._use_van()
        elif name == "casino_door":
            self.app.push_state("casino_interior")
        elif name == "shady_man":
            self.app.push_state("shop")

    def _use_van(self):
        if self.map_name == "home":
            self._load_map("casino_area", spawn=MAPS["casino_area"]["spawn"])
        else:
            self._load_map("home", spawn=MAPS["home"]["spawn"])

    def handle_event(self, event):
        if self.handle_topdown_event(event):
            return
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.app.push_state("pause_menu")

    def update(self, dt):
        self.update_player(dt)

    def draw(self, surface):
        tile = self.floor_tile
        tw, th = tile.get_size()
        for ty in range(0, C.INTERNAL_HEIGHT, th):
            for tx in range(0, C.INTERNAL_WIDTH, tw):
                surface.blit(tile, (tx, ty))

        for obs in self.map.get("obstacles", []):
            pygame.draw.rect(surface, (58, 46, 40), obs)
            pygame.draw.rect(surface, (30, 24, 20), obs, 2)

        if self.map_name == "casino_area":
            facade = get_casino_facade(width_tiles=15, height_tiles=8, pixel_size=1)
            building = self.map["obstacles"][0]
            fw, fh = facade.get_size()
            surface.blit(facade, (building.centerx - fw // 2, building.bottom - fh))
            shady = self.map["shady_man"]
            npc = get_shady_man_sprite(pixel_size=2)
            surface.blit(npc, (shady.centerx - npc.get_width() // 2, shady.centery - npc.get_height() // 2))

        van = self.map.get("van")
        if van:
            van_sprite = get_van_sprite(pixel_size=2)
            surface.blit(van_sprite, (van.centerx - van_sprite.get_width() // 2,
                                       van.centery - van_sprite.get_height() // 2))

        self.draw_player(surface)

        player = self.app.player
        if self.prompt:
            label = {"van": "Enter Van [E]", "casino_door": "Enter Casino [E]",
                      "shady_man": "Talk [E]"}[self.prompt]
            draw_text(surface, label, (int(player.x), int(player.y) - 22), size=8, color=C.GOLD, center=True)

        draw_text(surface, self.map["label"], (6, 4), size=9, color=C.UI_TEXT_DIM)
        draw_text(surface, f"Chips: {player.chips}", (6, C.INTERNAL_HEIGHT - 12), size=9, color=C.GOLD)
        draw_text(surface, "ESC: Menu", (C.INTERNAL_WIDTH - 50, C.INTERNAL_HEIGHT - 12), size=7,
                  color=C.UI_TEXT_DIM)
