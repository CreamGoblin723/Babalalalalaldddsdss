import pygame

from game import constants as C
from game import game_flow
from game.states.base import State
from game.ui import Button, draw_text
from game.sprites import get_roulette_wheel_sprite, get_number_badge
from game.abilities import wheel_whisperer_bias
from game import roulette_logic as roulette

BET_LABELS = {
    "red": "RED", "black": "BLACK", "green": "0 (35x)",
    "odd": "ODD", "even": "EVEN", "low": "1-18", "high": "19-36",
}


class RouletteState(State):
    def on_enter(self, **kwargs):
        self.phase = "betting"  # betting -> spinning -> result
        self.bet = min(50, self.app.player.chips) or 10
        self.choice = "red"
        self.number = None
        self.spin_timer = 0.0
        self.spin_duration = 1.1
        self.wheel_angle = 0.0
        self.result_text = ""
        self.result_color = C.UI_TEXT
        self._build_buttons()

    def on_resume(self, **kwargs):
        pass

    def _build_buttons(self):
        h = 14
        y1 = C.INTERNAL_HEIGHT - 60
        y2 = C.INTERNAL_HEIGHT - 42
        self.bet_buttons = {
            "red": Button((10, y1, 70, h), "RED", self._pick("red"), size=8),
            "black": Button((84, y1, 70, h), "BLACK", self._pick("black"), size=8),
            "green": Button((158, y1, 70, h), "0 (35x)", self._pick("green"), size=8),
            "odd": Button((10, y2, 70, h), "ODD", self._pick("odd"), size=8),
            "even": Button((84, y2, 70, h), "EVEN", self._pick("even"), size=8),
            "low": Button((158, y2, 76, h), "1-18", self._pick("low"), size=8),
            "high": Button((238, y2, 76, h), "19-36", self._pick("high"), size=8),
        }
        y = C.INTERNAL_HEIGHT - 22
        self.bet_minus = Button((20, y, 26, 16), "-", self._dec_bet, size=10)
        self.bet_plus = Button((50, y, 26, 16), "+", self._inc_bet, size=10)
        self.spin_btn = Button((150, y, 54, 16), "SPIN", self._spin, size=10)
        self.leave_btn = Button((C.INTERNAL_WIDTH - 58, y, 50, 16), "LEAVE", self._leave, size=9)
        self.play_again_btn = Button((60, y, 90, 16), "PLAY AGAIN", self._reset_for_bet, size=9)

    def _pick(self, choice):
        def _inner():
            self.choice = choice
        return _inner

    def _dec_bet(self):
        self.bet = max(10, self.bet - 10)

    def _inc_bet(self):
        self.bet = min(self.app.player.chips, self.bet + 10)

    def _spin(self):
        player = self.app.player
        if self.bet <= 0 or self.bet > player.chips:
            return
        player.add_chips(-self.bet)
        player.hands_played += 1
        bias = wheel_whisperer_bias(player)
        self.number = roulette.spin(self.choice, bias)
        self.phase = "spinning"
        self.spin_timer = 0.0

    def _finish_spin(self):
        player = self.app.player
        won = roulette.bet_wins(self.choice, self.number)
        guaranteed = player.active_effects.pop("guaranteed_win", False)
        if guaranteed and not won:
            won = True
        color = roulette.number_color(self.number)
        if won:
            multiplier = roulette.PAYOUT_MULTIPLIER[self.choice]
            payout = self.bet * (multiplier + 1)
            player.add_chips(payout)
            self.result_text = f"{self.number} ({color})! You win +{payout - self.bet}c"
            self.result_color = C.GOLD if multiplier > 1 else C.NEON_GREEN
            player.games_won += 1
        else:
            self.result_text = f"{self.number} ({color}). You lost {self.bet}c."
            self.result_color = C.BLOOD_RED
            player.games_lost += 1
        self.phase = "result"
        game_flow.check_run_end(self.app)

    def _reset_for_bet(self):
        self.phase = "betting"
        self.bet = min(self.bet, max(10, self.app.player.chips))
        self.number = None

    def _leave(self):
        self.app.pop_state()

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self._leave()
            return
        player = self.app.player
        if self.phase == "betting":
            for b in self.bet_buttons.values():
                b.handle_event(event)
            self.bet_minus.handle_event(event)
            self.bet_plus.handle_event(event)
            self.spin_btn.handle_event(event)
            self.leave_btn.handle_event(event)
        elif self.phase == "result":
            self.play_again_btn.handle_event(event)
            self.leave_btn.handle_event(event)

    def update(self, dt):
        if self.phase == "spinning":
            self.spin_timer += dt
            self.wheel_angle = (self.wheel_angle + dt * 900 * (1.0 - self.spin_timer / self.spin_duration)) % 360
            if self.spin_timer >= self.spin_duration:
                self._finish_spin()

    def draw(self, surface):
        surface.fill((16, 30, 20))
        draw_text(surface, "ROULETTE", (C.INTERNAL_WIDTH // 2, 6), size=13, color=C.GOLD, center=True, bold=True)

        cx = C.INTERNAL_WIDTH // 2
        base_wheel = get_roulette_wheel_sprite(size=88)
        if self.phase == "spinning":
            wheel = pygame.transform.rotate(base_wheel, self.wheel_angle)
        else:
            wheel = base_wheel
        surface.blit(wheel, wheel.get_rect(center=(cx, 62)))

        if self.phase == "result" and self.number is not None:
            badge = get_number_badge(self.number, roulette.number_color(self.number), size=26)
            surface.blit(badge, badge.get_rect(center=(cx, 62)))

        player = self.app.player
        if self.phase == "betting":
            draw_text(surface, f"Betting on: {BET_LABELS[self.choice]}", (cx, 112), size=9,
                      color=C.NEON_GREEN, center=True)
            for key, b in self.bet_buttons.items():
                b.hovered = b.hovered or (self.choice == key)
                b.draw(surface)
            draw_text(surface, f"Bet: {self.bet}c", (82, C.INTERNAL_HEIGHT - 19), size=9, color=C.GOLD)
            self.bet_minus.draw(surface)
            self.bet_plus.draw(surface)
            self.spin_btn.enabled = 10 <= self.bet <= player.chips
            self.spin_btn.draw(surface)
            self.leave_btn.draw(surface)
        elif self.phase == "spinning":
            draw_text(surface, "Spinning...", (cx, 112), size=10, center=True)
        elif self.phase == "result":
            draw_text(surface, self.result_text, (cx, C.INTERNAL_HEIGHT - 66), size=10,
                      color=self.result_color, center=True)
            self.play_again_btn.draw(surface)
            self.leave_btn.draw(surface)

        draw_text(surface, f"Chips: {player.chips}", (C.INTERNAL_WIDTH - 90, 4), size=9, color=C.GOLD)
