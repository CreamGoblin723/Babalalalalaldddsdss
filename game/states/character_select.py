import pygame

from game import constants as C
from game import save_manager
from game import game_flow
from game.states.base import State
from game.ui import Button, draw_text, draw_panel
from game.sprites import get_character_sprite, SKIN_ORDER, SKIN_NAMES, SKIN_COSTS


class CharacterSelectState(State):
    def on_enter(self, **kwargs):
        self.meta = save_manager.load_meta()
        self.skin_index = 0
        self.name = "Drifter"
        self.editing_name = True
        self._skip_to_unlocked()
        self._build_buttons()

    def _unlocked_skins(self):
        return self.meta.get("unlocked_skins", ["drifter"])

    def _skip_to_unlocked(self):
        pass  # locked skins are shown too (purchasable), no need to skip

    def _build_buttons(self):
        cy = 90
        self.left_btn = Button((60, cy - 8, 20, 20), "<", self._prev_skin)
        self.right_btn = Button((C.INTERNAL_WIDTH - 80, cy - 8, 20, 20), ">", self._next_skin)
        self.unlock_btn = Button((C.INTERNAL_WIDTH // 2 - 45, 150, 90, 16), "UNLOCK", self._unlock, size=9)
        self.start_btn = Button((C.INTERNAL_WIDTH // 2 - 55, 185, 110, 20), "START RUN", self._start)
        self.back_btn = Button((10, C.INTERNAL_HEIGHT - 24, 60, 16), "BACK", self._back, size=9)

    def _prev_skin(self):
        self.skin_index = (self.skin_index - 1) % len(SKIN_ORDER)

    def _next_skin(self):
        self.skin_index = (self.skin_index + 1) % len(SKIN_ORDER)

    def _current_skin(self):
        return SKIN_ORDER[self.skin_index]

    def _unlock(self):
        skin = self._current_skin()
        if skin in self._unlocked_skins():
            return
        cost = SKIN_COSTS.get(skin, 0)
        if self.meta.get("blood_money", 0) >= cost:
            self.meta["blood_money"] -= cost
            self.meta.setdefault("unlocked_skins", []).append(skin)
            save_manager.save_meta(self.meta)
            self.app.meta = self.meta

    def _start(self):
        skin = self._current_skin()
        if skin not in self._unlocked_skins():
            return
        name = self.name.strip() or "Drifter"
        game_flow.start_new_game(self.app, name, skin)

    def _back(self):
        self.app.pop_state()

    def handle_event(self, event):
        self.left_btn.handle_event(event)
        self.right_btn.handle_event(event)
        self.unlock_btn.handle_event(event)
        self.start_btn.handle_event(event)
        self.back_btn.handle_event(event)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self._back()
            elif event.key == pygame.K_LEFT:
                self._prev_skin()
            elif event.key == pygame.K_RIGHT:
                self._next_skin()
            elif event.key == pygame.K_RETURN:
                self._start()
            elif event.key == pygame.K_BACKSPACE:
                self.name = self.name[:-1]
            elif event.unicode and event.unicode.isprintable() and len(self.name) < 14:
                self.name += event.unicode

    def draw(self, surface):
        surface.fill((16, 14, 22))
        draw_text(surface, "CHOOSE YOUR GAMBLER", (C.INTERNAL_WIDTH // 2, 10), size=14,
                  color=C.GOLD, center=True, bold=True)

        # name box
        box = pygame.Rect(C.INTERNAL_WIDTH // 2 - 70, 22, 140, 16)
        draw_panel(surface, box, bg=(24, 22, 30))
        draw_text(surface, self.name + ("_" if int(pygame.time.get_ticks() / 400) % 2 == 0 else ""),
                  (box.centerx, box.centery), size=10, center=True)

        skin = self._current_skin()
        sprite = get_character_sprite(skin, "down", 0, pixel_size=5)
        rect = sprite.get_rect(center=(C.INTERNAL_WIDTH // 2, 95))
        surface.blit(sprite, rect)

        self.left_btn.draw(surface)
        self.right_btn.draw(surface)

        unlocked = skin in self._unlocked_skins()
        draw_text(surface, SKIN_NAMES.get(skin, skin), (C.INTERNAL_WIDTH // 2, 130), size=12,
                  color=C.UI_TEXT, center=True)

        if unlocked:
            draw_text(surface, "unlocked", (C.INTERNAL_WIDTH // 2, 144), size=9,
                      color=C.NEON_GREEN, center=True)
        else:
            cost = SKIN_COSTS.get(skin, 0)
            afford = self.meta.get("blood_money", 0) >= cost
            draw_text(surface, f"{cost} Blood Money", (C.INTERNAL_WIDTH // 2, 144), size=9,
                      color=C.GOLD if afford else C.UI_TEXT_DIM, center=True)
            self.unlock_btn.enabled = afford
            self.unlock_btn.draw(surface)

        self.start_btn.enabled = unlocked
        self.start_btn.draw(surface)
        self.back_btn.draw(surface)

        draw_text(surface, f"Blood Money: {self.meta.get('blood_money', 0)}", (6, 6),
                  size=8, color=C.GOLD)
