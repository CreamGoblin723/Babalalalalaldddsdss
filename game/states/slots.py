import random
import pygame

from game import constants as C
from game import game_flow
from game.states.base import State
from game.ui import Button, draw_text, draw_panel
from game.sprites import get_slot_symbol
from game.abilities import rigged_reels_bias
from game import slots_logic as slots

SYMBOL_ORDER = list(slots.BASE_WEIGHTS.keys())


class SlotsState(State):
    def on_enter(self, **kwargs):
        self.phase = "betting"  # betting -> spinning -> result
        self.bet = min(50, self.app.player.chips) or 10
        self.reels = ("cherry", "bell", "bar")
        self.display_reels = list(self.reels)
        self.spin_timer = 0.0
        self.spin_duration = 0.9
        self.result_text = ""
        self.result_color = C.UI_TEXT
        self._build_buttons()

    def on_resume(self, **kwargs):
        pass

    def _build_buttons(self):
        h = 16
        y = C.INTERNAL_HEIGHT - 22
        self.bet_minus = Button((20, y, 26, h), "-", self._dec_bet, size=10)
        self.bet_plus = Button((50, y, 26, h), "+", self._inc_bet, size=10)
        self.spin_btn = Button((150, y, 54, h), "SPIN", self._spin, size=10)
        self.leave_btn = Button((C.INTERNAL_WIDTH - 58, y, 50, h), "LEAVE", self._leave, size=9)
        self.play_again_btn = Button((60, y, 90, h), "PLAY AGAIN", self._reset_for_bet, size=9)
        item_y = y - 18
        self.rabbit_btn = Button((C.INTERNAL_WIDTH // 2 - 55, item_y, 110, 14), "USE RABBIT'S FOOT",
                                  self._use_rabbit, size=7)

    def _dec_bet(self):
        self.bet = max(10, self.bet - 10)

    def _inc_bet(self):
        self.bet = min(self.app.player.chips, self.bet + 10)

    def _use_rabbit(self):
        p = self.app.player
        if p.use_item("rabbits_foot"):
            p.active_effects["guaranteed_win"] = True

    def _spin(self):
        player = self.app.player
        if self.bet <= 0 or self.bet > player.chips:
            return
        player.add_chips(-self.bet)
        player.hands_played += 1
        bias = rigged_reels_bias(player)
        self.reels = slots.spin_reels(bias)
        self.phase = "spinning"
        self.spin_timer = 0.0

    def _finish_spin(self):
        player = self.app.player
        multiplier = slots.resolve_spin(self.reels)
        guaranteed = player.active_effects.pop("guaranteed_win", False)
        if guaranteed and multiplier <= 0:
            multiplier = 2
        if multiplier > 0:
            payout = self.bet * multiplier
            player.add_chips(payout)
            self.result_text = f"{multiplier}x! You win +{payout - self.bet}c"
            self.result_color = C.NEON_GREEN if multiplier < 10 else C.GOLD
            player.games_won += 1
        else:
            self.result_text = f"No match. You lost {self.bet}c."
            self.result_color = C.BLOOD_RED
            player.games_lost += 1
        self.phase = "result"
        game_flow.check_run_end(self.app)

    def _reset_for_bet(self):
        self.phase = "betting"
        self.bet = min(self.bet, max(10, self.app.player.chips))

    def _leave(self):
        self.app.pop_state()

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self._leave()
            return
        player = self.app.player
        if self.phase == "betting":
            self.bet_minus.handle_event(event)
            self.bet_plus.handle_event(event)
            self.spin_btn.handle_event(event)
            self.leave_btn.handle_event(event)
            if player.item_count("rabbits_foot") > 0:
                self.rabbit_btn.handle_event(event)
        elif self.phase == "result":
            self.play_again_btn.handle_event(event)
            self.leave_btn.handle_event(event)

    def update(self, dt):
        if self.phase == "spinning":
            self.spin_timer += dt
            if int(self.spin_timer * 20) % 2 == 0:
                self.display_reels = [random.choice(SYMBOL_ORDER) for _ in range(3)]
            # reels lock left-to-right as the timer runs out, like a real machine
            locked = min(3, int(self.spin_timer / self.spin_duration * 4))
            for i in range(min(locked, 3)):
                self.display_reels[i] = self.reels[i]
            if self.spin_timer >= self.spin_duration:
                self.display_reels = list(self.reels)
                self._finish_spin()

    def draw(self, surface):
        surface.fill((22, 16, 30))
        draw_text(surface, "SLOTS", (C.INTERNAL_WIDTH // 2, 6), size=13, color=C.GOLD, center=True, bold=True)

        cx = C.INTERNAL_WIDTH // 2
        window = pygame.Rect(cx - 60, 26, 120, 44)
        draw_panel(surface, window, bg=(20, 18, 26))
        for i in range(1, 3):
            lx = window.x + i * window.w // 3
            pygame.draw.line(surface, C.UI_BORDER, (lx, window.y + 3), (lx, window.bottom - 3))

        reels = self.display_reels if self.phase != "betting" else list(self.reels)
        gap = window.w // 3
        for i, sym in enumerate(reels):
            icon = get_slot_symbol(sym, size=32)
            x = window.x + gap // 2 + i * gap
            surface.blit(icon, icon.get_rect(center=(x, window.centery)))

        if self.phase == "betting":
            draw_text(surface, "3 match pays big - 2 cherries pay a little.", (cx, 78), size=7,
                      color=C.UI_TEXT_DIM, center=True)

        player = self.app.player
        if self.phase == "betting":
            draw_text(surface, f"Bet: {self.bet}c", (82, C.INTERNAL_HEIGHT - 19), size=9, color=C.GOLD)
            self.bet_minus.draw(surface)
            self.bet_plus.draw(surface)
            self.spin_btn.enabled = 10 <= self.bet <= player.chips
            self.spin_btn.draw(surface)
            self.leave_btn.draw(surface)
            if player.item_count("rabbits_foot") > 0:
                self.rabbit_btn.draw(surface)
        elif self.phase == "spinning":
            draw_text(surface, "Spinning...", (cx, 100), size=10, center=True)
        elif self.phase == "result":
            draw_text(surface, self.result_text, (cx, C.INTERNAL_HEIGHT - 66), size=10,
                      color=self.result_color, center=True)
            self.play_again_btn.draw(surface)
            self.leave_btn.draw(surface)

        draw_text(surface, f"Chips: {player.chips}", (C.INTERNAL_WIDTH - 90, 4), size=9, color=C.GOLD)
