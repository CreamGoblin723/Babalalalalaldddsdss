import pygame

from game import constants as C
from game.states.topdown import TopDownState
from game.ui import draw_text
from game.sprites import get_table_sprite, get_floor_tile

TABLES = {
    "blackjack": {"pos": (70, 90), "label": "Blackjack", "state": "blackjack"},
    "coinflip": {"pos": (160, 60), "label": "Coin Flip", "state": "coinflip"},
    "overunder": {"pos": (250, 90), "label": "Over/Under", "state": "overunder"},
}

TABLE_HITBOX = 20


class CasinoInteriorState(TopDownState):
    def on_enter(self, **kwargs):
        self.bounds = pygame.Rect(10, 26, C.INTERNAL_WIDTH - 20, C.INTERNAL_HEIGHT - 46)
        self.obstacles = []
        self.exit_zone = pygame.Rect(C.INTERNAL_WIDTH // 2 - 16, C.INTERNAL_HEIGHT - 24, 32, 14)
        self.floor_tile = get_floor_tile("carpet", pixel_size=1, size=16)
        player = self.app.player
        # once-per-visit ability charges (Second Chance, Double Take) reset
        # every time you step onto the casino floor
        player.active_effects = {}
        player.x, player.y = C.INTERNAL_WIDTH // 2, C.INTERNAL_HEIGHT - 40

    def on_resume(self, **kwargs):
        pass

    def interact_zones(self):
        zones = {"exit": self.exit_zone}
        for key, table in TABLES.items():
            tx, ty = table["pos"]
            zones[key] = pygame.Rect(tx - TABLE_HITBOX, ty - TABLE_HITBOX, TABLE_HITBOX * 2, TABLE_HITBOX * 2)
        return zones

    def on_interact(self, name):
        if name == "exit":
            self.app.pop_state()
        elif name in TABLES:
            self.app.push_state(TABLES[name]["state"])

    def handle_event(self, event):
        if self.handle_topdown_event(event):
            return
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.app.push_state("pause_menu")

    def update(self, dt):
        self.update_player(dt)

    def draw(self, surface):
        surface.fill((20, 16, 24))
        tile = self.floor_tile
        tw, th = tile.get_size()
        floor_rect = self.bounds
        for ty in range(floor_rect.top, floor_rect.bottom, th):
            for tx in range(floor_rect.left, floor_rect.right, tw):
                surface.blit(tile, (tx, ty))
        pygame.draw.rect(surface, (58, 36, 26), floor_rect, 3)

        for key, table in TABLES.items():
            sprite = get_table_sprite(key, pixel_size=1)
            rect = sprite.get_rect(center=table["pos"])
            surface.blit(sprite, rect)
            draw_text(surface, table["label"], (table["pos"][0], table["pos"][1] - 22), size=8,
                      color=C.UI_TEXT, center=True)

        pygame.draw.rect(surface, (30, 26, 20), self.exit_zone)
        draw_text(surface, "EXIT", self.exit_zone.center, size=8, color=C.GOLD, center=True)

        self.draw_player(surface)

        player = self.app.player
        if self.prompt:
            label = "Leave [E]" if self.prompt == "exit" else f"Play {TABLES[self.prompt]['label']} [E]"
            draw_text(surface, label, (int(player.x), int(player.y) - 22), size=8, color=C.GOLD, center=True)

        draw_text(surface, "Casino Floor", (6, 4), size=9, color=C.UI_TEXT_DIM)
        draw_text(surface, f"Chips: {player.chips}", (6, C.INTERNAL_HEIGHT - 12), size=9, color=C.GOLD)
