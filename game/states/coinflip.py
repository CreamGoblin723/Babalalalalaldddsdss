import random
import pygame

from game import constants as C
from game import game_flow
from game.states.base import State
from game.ui import Button, draw_text
from game.sprites import get_coin_sprite
from game.abilities import biased_coin


class CoinFlipState(State):
    def on_enter(self, **kwargs):
        self.phase = "betting"  # betting -> flipping -> result
        self.bet = min(50, self.app.player.chips) or 10
        self.choice = "heads"
        self.flip_timer = 0.0
        self.flip_duration = 0.9
        self.display_face = "heads"
        self.result_face = None
        self.result_text = ""
        self.result_color = C.UI_TEXT
        self.double_take_offered = False
        self._build_buttons()

    def on_resume(self, **kwargs):
        pass

    def _build_buttons(self):
        w, h = 40, 16
        y = C.INTERNAL_HEIGHT - 22
        self.bet_minus = Button((40, y, w, h), "-", self._dec_bet, size=10)
        self.bet_plus = Button((84, y, w, h), "+", self._inc_bet, size=10)
        self.heads_btn = Button((130, y, 60, h), "HEADS", self._pick_heads, size=9)
        self.tails_btn = Button((194, y, 60, h), "TAILS", self._pick_tails, size=9)
        self.flip_btn = Button((C.INTERNAL_WIDTH // 2 - 30, y - 22, 60, h), "FLIP!", self._flip, size=10)
        self.leave_btn = Button((C.INTERNAL_WIDTH - 60, y, 52, h), "LEAVE", self._leave, size=9)
        self.play_again_btn = Button((60, y, 90, h), "PLAY AGAIN", self._reset_for_bet, size=9)
        self.call_again_btn = Button((C.INTERNAL_WIDTH // 2 - 55, y - 22, 110, h), "CALL AGAIN (FREE)",
                                      self._call_again, size=8)

    def _dec_bet(self):
        self.bet = max(10, self.bet - 10)

    def _inc_bet(self):
        self.bet = min(self.app.player.chips, self.bet + 10)

    def _pick_heads(self):
        self.choice = "heads"

    def _pick_tails(self):
        self.choice = "tails"

    def _flip(self):
        player = self.app.player
        if self.bet <= 0 or self.bet > player.chips:
            return
        player.add_chips(-self.bet)
        player.hands_played += 1
        self._resolve_flip()

    def _resolve_flip(self):
        prob_player = biased_coin(self.app.player)
        landed_player_side = random.random() < prob_player
        self.result_face = self.choice if landed_player_side else self._other(self.choice)
        self.phase = "flipping"
        self.flip_timer = 0.0

    def _other(self, face):
        return "tails" if face == "heads" else "heads"

    def _call_again(self):
        player = self.app.player
        if player.active_effects.get("double_take_used"):
            return
        player.active_effects["double_take_used"] = True
        self.double_take_offered = False
        self._resolve_flip()

    def _finish_flip(self):
        player = self.app.player
        won = self.result_face == self.choice
        guaranteed = player.active_effects.pop("guaranteed_win", False)
        if guaranteed and not won:
            won = True
        if won:
            player.add_chips(self.bet * 2)
            self.result_text = f"{self.result_face.upper()}! You win +{self.bet}c"
            self.result_color = C.NEON_GREEN
            player.games_won += 1
            self.phase = "result"
        else:
            player.games_lost += 1
            if (player.has_ability("double_take")
                    and not player.active_effects.get("double_take_used")):
                self.result_text = f"{self.result_face.upper()}. You lost {self.bet}c."
                self.result_color = C.BLOOD_RED
                self.double_take_offered = True
                self.phase = "result"
            else:
                self.result_text = f"{self.result_face.upper()}. You lost {self.bet}c."
                self.result_color = C.BLOOD_RED
                self.phase = "result"
        game_flow.check_run_end(self.app)

    def _reset_for_bet(self):
        self.phase = "betting"
        self.double_take_offered = False
        self.bet = min(self.bet, max(10, self.app.player.chips))

    def _leave(self):
        self.app.pop_state()

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self._leave()
            return
        if self.phase == "betting":
            self.bet_minus.handle_event(event)
            self.bet_plus.handle_event(event)
            self.heads_btn.handle_event(event)
            self.tails_btn.handle_event(event)
            self.flip_btn.handle_event(event)
            self.leave_btn.handle_event(event)
        elif self.phase == "result":
            self.play_again_btn.handle_event(event)
            self.leave_btn.handle_event(event)
            if self.double_take_offered:
                self.call_again_btn.handle_event(event)

    def update(self, dt):
        if self.phase == "flipping":
            self.flip_timer += dt
            flicker_index = int(self.flip_timer * 14) % 2
            self.display_face = "heads" if flicker_index == 0 else "tails"
            if self.flip_timer >= self.flip_duration:
                self.display_face = self.result_face
                self._finish_flip()

    def draw(self, surface):
        surface.fill((18, 22, 46))
        draw_text(surface, "COIN FLIP", (C.INTERNAL_WIDTH // 2, 6), size=13, color=C.GOLD, center=True, bold=True)

        face = self.display_face if self.phase == "flipping" else (self.result_face or self.choice)
        coin = get_coin_sprite(face, radius=26)
        surface.blit(coin, coin.get_rect(center=(C.INTERNAL_WIDTH // 2, 75)))

        player = self.app.player
        if self.phase == "betting":
            draw_text(surface, f"Bet: {self.bet}c", (40, C.INTERNAL_HEIGHT - 42), size=11, color=C.GOLD)
            draw_text(surface, f"Calling: {self.choice.upper()}", (130, 110), size=10, color=C.UI_TEXT, center=False)
            self.bet_minus.draw(surface)
            self.bet_plus.draw(surface)
            self.heads_btn.draw(surface)
            self.tails_btn.draw(surface)
            self.flip_btn.enabled = 10 <= self.bet <= player.chips
            self.flip_btn.draw(surface)
            self.leave_btn.draw(surface)
        elif self.phase == "flipping":
            draw_text(surface, "Flipping...", (C.INTERNAL_WIDTH // 2, 115), size=10, center=True)
        elif self.phase == "result":
            draw_text(surface, self.result_text, (C.INTERNAL_WIDTH // 2, C.INTERNAL_HEIGHT - 66), size=10,
                      color=self.result_color, center=True)
            if self.double_take_offered:
                self.call_again_btn.draw(surface)
            self.play_again_btn.draw(surface)
            self.leave_btn.draw(surface)

        draw_text(surface, f"Chips: {player.chips}", (C.INTERNAL_WIDTH - 90, 4), size=9, color=C.GOLD)
