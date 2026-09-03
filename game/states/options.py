import pygame

from game import constants as C
from game import settings_manager
from game.states.base import State
from game.ui import Button, Slider, draw_text, navigate_buttons


class OptionsState(State):
    def on_enter(self, **kwargs):
        self.settings = self.app.settings
        w = 140
        x = C.INTERNAL_WIDTH // 2 - w // 2
        self.volume_slider = Slider((x, 60, w, 12), value=self.settings.get("master_volume", 0.7),
                                     on_change=self._set_volume)
        self.fullscreen_btn = Button((x, 90, w, 18), self._fs_label(), self._toggle_fullscreen, size=10)
        self.back_btn = Button((C.INTERNAL_WIDTH // 2 - 40, 130, 80, 18), "BACK", self._back)
        self.nav_buttons = [self.fullscreen_btn, self.back_btn]
        self.selected = 0

    def _fs_label(self):
        return "FULLSCREEN: ON" if self.settings.get("fullscreen") else "FULLSCREEN: OFF"

    def _set_volume(self, value):
        self.settings["master_volume"] = value
        try:
            pygame.mixer.music.set_volume(value)
        except pygame.error:
            pass
        settings_manager.save_settings(self.settings)

    def _toggle_fullscreen(self):
        self.app.toggle_fullscreen()
        self.fullscreen_btn.label = self._fs_label()

    def _back(self):
        self.app.pop_state()

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self._back()
            return
        self.volume_slider.handle_event(event)
        self.fullscreen_btn.handle_event(event)
        self.back_btn.handle_event(event)
        if event.type == pygame.KEYDOWN and event.key in (pygame.K_LEFT, pygame.K_RIGHT):
            step = -0.05 if event.key == pygame.K_LEFT else 0.05
            self.volume_slider.value = max(0.0, min(1.0, self.volume_slider.value + step))
            self._set_volume(self.volume_slider.value)
        else:
            self.selected, _ = navigate_buttons(self.nav_buttons, self.selected, event)

    def draw(self, surface):
        surface.fill((16, 14, 22))
        draw_text(surface, "OPTIONS", (C.INTERNAL_WIDTH // 2, 20), size=16, color=C.GOLD, center=True, bold=True)
        draw_text(surface, "Master Volume", (C.INTERNAL_WIDTH // 2, 50), size=9, center=True)
        self.volume_slider.draw(surface)
        for i, b in enumerate(self.nav_buttons):
            b.hovered = b.hovered or i == self.selected
            b.draw(surface)
        draw_text(surface, "(F11 also toggles fullscreen anywhere)", (C.INTERNAL_WIDTH // 2, 112), size=7,
                  color=C.UI_TEXT_DIM, center=True)
