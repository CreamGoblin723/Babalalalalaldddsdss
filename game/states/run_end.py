import pygame

from game import constants as C
from game.states.base import State
from game.ui import Button, draw_text


class RunEndState(State):
    def on_enter(self, victory=False, blood_money_earned=0, player=None, **kwargs):
        self.victory = victory
        self.blood_money_earned = blood_money_earned
        self.player = player
        w = 100
        self.menu_btn = Button((C.INTERNAL_WIDTH // 2 - w // 2, 170, w, 20), "MAIN MENU", self._to_menu)

    def _to_menu(self):
        self.app.player = None
        self.app.active_slot = None
        self.app.switch_state("main_menu")

    def handle_event(self, event):
        self.menu_btn.handle_event(event)
        if event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_ESCAPE):
            self._to_menu()

    def draw(self, surface):
        if self.victory:
            surface.fill((30, 26, 10))
            title = "YOU BEAT THE HOUSE"
            color = C.GOLD
        else:
            surface.fill((28, 8, 10))
            title = "BUSTED OUT"
            color = C.BLOOD_RED

        draw_text(surface, title, (C.INTERNAL_WIDTH // 2, 40), size=18, color=color, center=True, bold=True)

        if self.victory:
            draw_text(surface, "You reached 1,000,000 chips.", (C.INTERNAL_WIDTH // 2, 66), size=10,
                      color=C.UI_TEXT, center=True)
            draw_text(surface, "The shady man tips his hat. Somewhere, a van drives away.",
                      (C.INTERNAL_WIDTH // 2, 80), size=8, color=C.UI_TEXT_DIM, center=True)
        else:
            draw_text(surface, "Your chips hit zero. The run is over.", (C.INTERNAL_WIDTH // 2, 66), size=10,
                      color=C.UI_TEXT, center=True)

        if self.player:
            draw_text(surface, f"Peak Chips: {self.player.peak_chips}", (C.INTERNAL_WIDTH // 2, 104), size=10,
                      color=C.UI_TEXT, center=True)
            draw_text(surface, f"Hands Played: {self.player.hands_played}  |  W:{self.player.games_won} "
                                f"L:{self.player.games_lost}", (C.INTERNAL_WIDTH // 2, 118), size=8,
                      color=C.UI_TEXT_DIM, center=True)

        draw_text(surface, f"+{self.blood_money_earned} Blood Money earned", (C.INTERNAL_WIDTH // 2, 140),
                  size=12, color=C.GOLD, center=True)

        self.menu_btn.draw(surface)
