import pygame

from game import constants as C
from game import save_manager
from game import game_flow
from game.states.base import State
from game.ui import Button, draw_text, navigate_buttons


class MainMenuState(State):
    def on_enter(self, **kwargs):
        self.buttons = []
        self._build_buttons()
        self._t = 0.0

    def on_resume(self, **kwargs):
        self._build_buttons()

    def _build_buttons(self):
        continue_slot = save_manager.get_continue_slot()
        w, h = 160, 20
        x = C.INTERNAL_WIDTH // 2 - w // 2
        y = 78
        gap = 24
        self.buttons = [
            Button((x, y, w, h), "CONTINUE", self._continue, enabled=continue_slot is not None),
            Button((x, y + gap, w, h), "LOAD GAME", self._load),
            Button((x, y + gap * 2, w, h), "NEW GAME", self._new_game),
            Button((x, y + gap * 3, w, h), "OPTIONS", self._options),
            Button((x, y + gap * 4, w, h), "EXIT", self._exit),
        ]
        self.selected = 1 if continue_slot is None else 0

    def _continue(self):
        slot = save_manager.get_continue_slot()
        if slot is None:
            return
        game_flow.resume_playthrough(self.app, slot)

    def _load(self):
        self.app.push_state("load_menu")

    def _new_game(self):
        self.app.push_state("character_select")

    def _options(self):
        self.app.push_state("options")

    def _exit(self):
        self.app.quit()

    def handle_event(self, event):
        for b in self.buttons:
            b.handle_event(event)
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.app.quit()
            return
        self.selected, _ = navigate_buttons(self.buttons, self.selected, event)

    def update(self, dt):
        self._t += dt

    def draw(self, surface):
        surface.fill((16, 14, 22))
        # simple night skyline / neon backdrop
        for i in range(0, C.INTERNAL_WIDTH, 40):
            h = 40 + (i * 37) % 60
            pygame.draw.rect(surface, (26, 22, 36), (i, C.INTERNAL_HEIGHT - h, 34, h))
        glow = abs(int(60 + 40 * pygame.math.Vector2(1, 0).rotate(self._t * 90).x))

        draw_text(surface, "BLOOD & CHIPS", (C.INTERNAL_WIDTH // 2, 40), size=24,
                  color=(min(255, 168 + glow // 2), 26, 34), bold=True, center=True)
        draw_text(surface, "a gambler's descent", (C.INTERNAL_WIDTH // 2, 58), size=9,
                  color=C.UI_TEXT_DIM, center=True)

        for i, b in enumerate(self.buttons):
            b.hovered = b.hovered or i == self.selected
            b.draw(surface)

        meta = self.app.meta
        draw_text(surface, f"Blood Money: {meta.get('blood_money', 0)}", (6, C.INTERNAL_HEIGHT - 12),
                  size=9, color=C.GOLD)
        draw_text(surface, "v1.0", (C.INTERNAL_WIDTH - 24, C.INTERNAL_HEIGHT - 12), size=9,
                  color=C.UI_TEXT_DIM)
