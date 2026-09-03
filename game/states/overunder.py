import pygame

from game import constants as C
from game import game_flow
from game.states.base import State
from game.ui import Button, draw_text
from game.sprites import get_die_face
from game.abilities import draw_die

CHOICES = ["under", "seven", "over"]


class OverUnderState(State):
    def on_enter(self, **kwargs):
        self.phase = "betting"  # betting -> rolling -> result
        self.bet = min(50, self.app.player.chips) or 10
        self.choice = "over"
        self.die1 = None
        self.die2 = None
        self.peeked = False
        self.roll_timer = 0.0
        self.roll_duration = 0.7
        self.result_text = ""
        self.result_color = C.UI_TEXT
        self._build_buttons()
        if self.app.player.has_ability("true_sight"):
            self._peek_die1()

    def on_resume(self, **kwargs):
        pass

    def _build_buttons(self):
        h = 16
        choice_y = C.INTERNAL_HEIGHT - 42
        self.under_btn = Button((10, choice_y, 96, h), "UNDER 7", self._pick("under"), size=8)
        self.seven_btn = Button((112, choice_y, 96, h), "= 7 (4x)", self._pick("seven"), size=8)
        self.over_btn = Button((214, choice_y, 96, h), "OVER 7", self._pick("over"), size=8)

        y = C.INTERNAL_HEIGHT - 22
        self.bet_minus = Button((10, y, 28, h), "-", self._dec_bet, size=10)
        self.bet_plus = Button((42, y, 28, h), "+", self._inc_bet, size=10)
        self.roll_btn = Button((174, y, 56, h), "ROLL", self._roll, size=10)
        self.leave_btn = Button((C.INTERNAL_WIDTH - 60, y, 50, h), "LEAVE", self._leave, size=9)
        self.play_again_btn = Button((60, y, 90, h), "PLAY AGAIN", self._reset_for_bet, size=9)

    def _pick(self, choice):
        def _inner():
            self.choice = choice
        return _inner

    def _dec_bet(self):
        self.bet = max(10, self.bet - 10)

    def _inc_bet(self):
        self.bet = min(self.app.player.chips, self.bet + 10)

    def _peek_die1(self):
        favor_high = self.choice == "over"
        self.die1 = draw_die(self.app.player, favor_high)
        self.peeked = True

    def _roll(self):
        player = self.app.player
        if self.bet <= 0 or self.bet > player.chips:
            return
        player.add_chips(-self.bet)
        player.hands_played += 1
        favor_high = self.choice == "over"
        if self.die1 is None:
            self.die1 = draw_die(player, favor_high)
        self.die2 = draw_die(player, favor_high)
        self.phase = "rolling"
        self.roll_timer = 0.0

    def _finish_roll(self):
        player = self.app.player
        total = self.die1 + self.die2
        won = ((self.choice == "over" and total > 7)
               or (self.choice == "under" and total < 7)
               or (self.choice == "seven" and total == 7))
        guaranteed = player.active_effects.pop("guaranteed_win", False)
        if guaranteed and not won:
            won = True
        if won:
            multiplier = 4 if self.choice == "seven" else 2
            payout = self.bet * multiplier
            player.add_chips(payout)
            self.result_text = f"Rolled {total}! You win +{payout - self.bet}c"
            self.result_color = C.NEON_GREEN
            player.games_won += 1
        else:
            self.result_text = f"Rolled {total}. You lost {self.bet}c."
            self.result_color = C.BLOOD_RED
            player.games_lost += 1
        self.phase = "result"
        game_flow.check_run_end(self.app)

    def _reset_for_bet(self):
        self.phase = "betting"
        self.bet = min(self.bet, max(10, self.app.player.chips))
        self.die1 = None
        self.die2 = None
        self.peeked = False
        if self.app.player.has_ability("true_sight"):
            self._peek_die1()

    def _leave(self):
        self.app.pop_state()

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self._leave()
            return
        if self.phase == "betting":
            self.bet_minus.handle_event(event)
            self.bet_plus.handle_event(event)
            self.under_btn.handle_event(event)
            self.seven_btn.handle_event(event)
            self.over_btn.handle_event(event)
            self.roll_btn.handle_event(event)
            self.leave_btn.handle_event(event)
        elif self.phase == "result":
            self.play_again_btn.handle_event(event)
            self.leave_btn.handle_event(event)

    def update(self, dt):
        if self.phase == "rolling":
            self.roll_timer += dt
            if self.roll_timer >= self.roll_duration:
                self._finish_roll()

    def draw(self, surface):
        surface.fill((46, 18, 26))
        draw_text(surface, "OVER / UNDER", (C.INTERNAL_WIDTH // 2, 6), size=13, color=C.GOLD, center=True, bold=True)
        draw_text(surface, "Two dice. Bet over, under, or exactly 7.", (C.INTERNAL_WIDTH // 2, 20), size=8,
                  color=C.UI_TEXT_DIM, center=True)

        cx = C.INTERNAL_WIDTH // 2
        if self.phase == "rolling":
            flicker = int(self.roll_timer * 16)
            d1 = (flicker + 1) % 6 + 1
            d2 = (flicker + 3) % 6 + 1
        else:
            d1 = self.die1 if self.die1 else (1 if self.peeked else 1)
            d2 = self.die2 if self.die2 else 1

        if self.die1 is not None or self.phase == "rolling":
            face1 = get_die_face(d1, size=36)
            surface.blit(face1, face1.get_rect(center=(cx - 26, 70)))
        if self.die2 is not None or self.phase == "rolling":
            face2 = get_die_face(d2, size=36)
            surface.blit(face2, face2.get_rect(center=(cx + 26, 70)))

        if self.phase == "betting" and self.peeked and self.die1 is not None:
            draw_text(surface, f"Peeked die: {self.die1}", (cx, 100), size=8, color=C.NEON_GREEN, center=True)

        player = self.app.player
        if self.phase == "betting":
            draw_text(surface, f"Bet: {self.bet}c", (80, C.INTERNAL_HEIGHT - 19), size=11, color=C.GOLD)
            for name, btn in (("under", self.under_btn), ("seven", self.seven_btn), ("over", self.over_btn)):
                btn.hovered = btn.hovered or (self.choice == name)
                btn.draw(surface)
            self.bet_minus.draw(surface)
            self.bet_plus.draw(surface)
            self.roll_btn.enabled = 10 <= self.bet <= player.chips
            self.roll_btn.draw(surface)
            self.leave_btn.draw(surface)
        elif self.phase == "rolling":
            draw_text(surface, "Rolling...", (cx, 115), size=10, center=True)
        elif self.phase == "result":
            draw_text(surface, self.result_text, (cx, C.INTERNAL_HEIGHT - 66), size=10,
                      color=self.result_color, center=True)
            self.play_again_btn.draw(surface)
            self.leave_btn.draw(surface)

        draw_text(surface, f"Chips: {player.chips}", (C.INTERNAL_WIDTH - 90, 4), size=9, color=C.GOLD)
