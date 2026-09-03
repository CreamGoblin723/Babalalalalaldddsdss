import pygame

from game import constants as C
from game import game_flow
from game.states.base import State
from game.ui import Button, draw_text, draw_panel, navigate_buttons


class PauseMenuState(State):
    def on_enter(self, **kwargs):
        w, h = 140, 20
        x = C.INTERNAL_WIDTH // 2 - w // 2
        y = 70
        gap = 26
        self.buttons = [
            Button((x, y, w, h), "RESUME", self._resume),
            Button((x, y + gap, w, h), "SAVE GAME", self._save),
            Button((x, y + gap * 2, w, h), "OPTIONS", self._options),
            Button((x, y + gap * 3, w, h), "QUIT TO MENU", self._quit_to_menu),
        ]
        self.message = ""
        self.message_timer = 0.0
        self.selected = 0

    def on_resume(self, **kwargs):
        pass

    def _resume(self):
        self.app.pop_state()

    def _save(self):
        game_flow.save_current(self.app)
        self.message = "Saved!"
        self.message_timer = 1.2

    def _options(self):
        self.app.push_state("options")

    def _quit_to_menu(self):
        game_flow.save_current(self.app)
        self.app.switch_state("main_menu")

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self._resume()
            return
        for b in self.buttons:
            b.handle_event(event)
        self.selected, _ = navigate_buttons(self.buttons, self.selected, event)

    def update(self, dt):
        if self.message_timer > 0:
            self.message_timer -= dt
            if self.message_timer <= 0:
                self.message = ""

    def draw(self, surface):
        overlay = pygame.Surface((C.INTERNAL_WIDTH, C.INTERNAL_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        surface.blit(overlay, (0, 0))

        panel = pygame.Rect(C.INTERNAL_WIDTH // 2 - 90, 30, 180, 160)
        draw_panel(surface, panel)
        draw_text(surface, "PAUSED", (C.INTERNAL_WIDTH // 2, 42), size=14, color=C.GOLD, center=True, bold=True)

        for i, b in enumerate(self.buttons):
            b.hovered = b.hovered or i == self.selected
            b.draw(surface)

        if self.message:
            draw_text(surface, self.message, (C.INTERNAL_WIDTH // 2, 185), size=10,
                      color=C.NEON_GREEN, center=True)
