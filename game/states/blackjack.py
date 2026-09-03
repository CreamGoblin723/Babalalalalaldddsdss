import pygame

from game import constants as C
from game import game_flow
from game.states.base import State
from game.ui import Button, draw_text
from game.sprites import get_playing_card
from game.abilities import card_counter_bust_reduction
from game import blackjack_logic as bj

BET_STEPS = [10, 25, 100, 500]


class BlackjackState(State):
    def on_enter(self, **kwargs):
        self.phase = "betting"  # betting -> player_turn -> dealer_turn -> result
        self.bet = min(50, self.app.player.chips) or 10
        self.player_hand = []
        self.dealer_hand = []
        self.result_text = ""
        self.result_color = C.UI_TEXT
        self.doubled = False
        self.session_second_chance_used = self.app.player.active_effects.get("second_chance_used", False)
        self._build_buttons()

    def on_resume(self, **kwargs):
        pass

    def _build_buttons(self):
        h = 16
        y = C.INTERNAL_HEIGHT - 22
        self.bet_minus = Button((20, y, 26, h), "-", self._dec_bet, size=10)
        self.bet_plus = Button((50, y, 26, h), "+", self._inc_bet, size=10)
        self.deal_btn = Button((140, y, 55, h), "DEAL", self._deal, size=10)
        self.leave_btn = Button((C.INTERNAL_WIDTH - 58, y, 50, h), "LEAVE", self._leave, size=9)

        self.hit_btn = Button((60, y, 50, h), "HIT", self._hit, size=10)
        self.stand_btn = Button((116, y, 60, h), "STAND", self._stand, size=10)
        self.double_btn = Button((182, y, 60, h), "DOUBLE", self._double, size=9)

        self.play_again_btn = Button((60, y, 90, h), "PLAY AGAIN", self._reset_for_bet, size=9)

        item_y = y - 20
        self.rabbit_btn = Button((60, item_y, 100, 14), "USE RABBIT'S FOOT", self._use_rabbit, size=7)
        self.deck_btn = Button((166, item_y, 100, 14), "USE MARKED DECK", self._use_deck, size=7)

    def _dec_bet(self):
        self.bet = max(10, self.bet - 10)

    def _inc_bet(self):
        self.bet = min(self.app.player.chips, self.bet + 10)

    def _use_rabbit(self):
        p = self.app.player
        if p.use_item("rabbits_foot"):
            p.active_effects["guaranteed_win"] = True

    def _use_deck(self):
        p = self.app.player
        if p.use_item("marked_deck"):
            p.active_effects["marked_deck"] = True

    def _bust_bias(self):
        return card_counter_bust_reduction(self.app.player)

    def _deal(self):
        player = self.app.player
        if self.bet <= 0 or self.bet > player.chips:
            return
        player.add_chips(-self.bet)
        player.hands_played += 1
        self.doubled = False

        if player.active_effects.pop("marked_deck", False):
            # guarantee a strong starting hand: build up to 19-21
            total_target = 19 + (hash(id(self)) % 3)  # 19,20,21 pseudo-varied
            self.player_hand = self._build_hand_worth(min(21, total_target))
        else:
            self.player_hand = [bj.draw_card(self._bust_bias()), bj.draw_card(self._bust_bias())]
        self.dealer_hand = [bj.draw_card(), bj.draw_card()]

        if bj.is_blackjack(self.player_hand) or bj.is_blackjack(self.dealer_hand):
            self.phase = "dealer_turn"
            self._resolve_dealer_turn(auto_from_blackjack=True)
        else:
            self.phase = "player_turn"

    def _build_hand_worth(self, target):
        # simple two-card combo close to target value
        if target >= 21:
            return [("A", "S"), ("K", "H")]
        first_val = min(10, target - 6)
        first_rank = "10" if first_val >= 10 else str(max(2, first_val))
        remaining = target - bj.rank_value(first_rank)
        second_rank = "10" if remaining >= 10 else str(max(2, remaining))
        return [(first_rank, "S"), (second_rank, "H")]

    def _hit(self):
        self.player_hand.append(bj.draw_card(self._bust_bias()))
        if bj.is_bust(self.player_hand):
            self._settle(player_busts=True)

    def _stand(self):
        self.phase = "dealer_turn"
        self._resolve_dealer_turn()

    def _double(self):
        player = self.app.player
        if player.chips < self.bet or len(self.player_hand) != 2:
            return
        player.add_chips(-self.bet)
        self.bet *= 2
        self.doubled = True
        self.player_hand.append(bj.draw_card(self._bust_bias()))
        if bj.is_bust(self.player_hand):
            self._settle(player_busts=True)
        else:
            self.phase = "dealer_turn"
            self._resolve_dealer_turn()

    def _resolve_dealer_turn(self, auto_from_blackjack=False):
        player_bj = bj.is_blackjack(self.player_hand)
        dealer_bj = bj.is_blackjack(self.dealer_hand)
        if auto_from_blackjack and (player_bj or dealer_bj):
            if player_bj and dealer_bj:
                self._settle(push=True)
            elif player_bj:
                self._settle(blackjack_win=True)
            else:
                self._settle(dealer_blackjack=True)
            return

        while bj.dealer_should_hit(self.dealer_hand):
            self.dealer_hand.append(bj.draw_card())

        if bj.is_bust(self.dealer_hand):
            self._settle(dealer_busts=True)
            return

        pv, dv = bj.hand_value(self.player_hand), bj.hand_value(self.dealer_hand)
        if pv > dv:
            self._settle(player_wins=True)
        elif pv < dv:
            self._settle(player_loses=True)
        else:
            self._settle(push=True)

    def _settle(self, player_busts=False, dealer_busts=False, player_wins=False,
                player_loses=False, push=False, blackjack_win=False, dealer_blackjack=False):
        player = self.app.player
        guaranteed = player.active_effects.pop("guaranteed_win", False)

        if player_busts and player.has_ability("second_chance") and not self.session_second_chance_used:
            self.session_second_chance_used = True
            player.active_effects["second_chance_used"] = True
            push = True
            player_busts = False

        if guaranteed and not (player_wins or blackjack_win):
            push = False
            player_loses = False
            dealer_busts = False
            player_wins = True

        if player_busts or player_loses:
            if dealer_blackjack and player.has_ability("insurance_hustle"):
                refund = self.bet // 2
                player.add_chips(refund)
                self.result_text = f"Dealer Blackjack. Insurance refunds {refund}c."
            else:
                self.result_text = "You busted!" if player_busts else "Dealer wins."
            self.result_color = C.BLOOD_RED
            player.games_lost += 1
        elif dealer_busts or player_wins:
            payout = self.bet * 2
            player.add_chips(payout)
            self.result_text = f"You win +{self.bet}c!"
            self.result_color = C.NEON_GREEN
            player.games_won += 1
        elif blackjack_win:
            payout = int(self.bet * 2.5)
            player.add_chips(payout)
            self.result_text = f"BLACKJACK! +{payout - self.bet}c"
            self.result_color = C.GOLD
            player.games_won += 1
        elif push:
            player.add_chips(self.bet)
            self.result_text = "Push. Bet returned."
            self.result_color = C.UI_TEXT_DIM
        self.phase = "result"
        game_flow.check_run_end(self.app)

    def _reset_for_bet(self):
        self.phase = "betting"
        self.bet = min(self.bet, max(10, self.app.player.chips))
        self.player_hand = []
        self.dealer_hand = []

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
            self.deal_btn.handle_event(event)
            self.leave_btn.handle_event(event)
            if player.item_count("rabbits_foot") > 0:
                self.rabbit_btn.handle_event(event)
            if player.item_count("marked_deck") > 0:
                self.deck_btn.handle_event(event)
        elif self.phase == "player_turn":
            self.hit_btn.handle_event(event)
            self.stand_btn.handle_event(event)
            if len(self.player_hand) == 2 and player.chips >= self.bet:
                self.double_btn.handle_event(event)
        elif self.phase == "result":
            self.play_again_btn.handle_event(event)
            self.leave_btn.handle_event(event)

    def update(self, dt):
        pass

    def _draw_hand(self, surface, cards, x, y, hide_second=False):
        for i, (rank, suit) in enumerate(cards):
            face_down = hide_second and i == 1
            card = get_playing_card(rank, suit, face_down=face_down, width=28, height=40)
            surface.blit(card, (x + i * 24, y))

    def draw(self, surface):
        surface.fill((14, 40, 28))
        draw_text(surface, "BLACKJACK", (C.INTERNAL_WIDTH // 2, 6), size=13, color=C.GOLD, center=True, bold=True)

        player = self.app.player
        hide_dealer = self.phase in ("betting", "player_turn") and not player.has_ability("sharp_eyes")
        if self.dealer_hand:
            self._draw_hand(surface, self.dealer_hand, 20, 24, hide_second=hide_dealer)
            dv = bj.hand_value(self.dealer_hand) if not hide_dealer else "?"
            draw_text(surface, f"Dealer: {dv}", (20, 66), size=9, color=C.UI_TEXT)
            if hide_dealer and player.has_ability("sharp_eyes"):
                pass

        if self.player_hand:
            self._draw_hand(surface, self.player_hand, 20, 110)
            draw_text(surface, f"You: {bj.hand_value(self.player_hand)}", (20, 152), size=9, color=C.UI_TEXT)

        if self.phase == "betting":
            draw_text(surface, f"Bet: {self.bet}c", (84, C.INTERNAL_HEIGHT - 19), size=9, color=C.GOLD)
            self.bet_minus.draw(surface)
            self.bet_plus.draw(surface)
            self.deal_btn.enabled = 10 <= self.bet <= player.chips
            self.deal_btn.draw(surface)
            self.leave_btn.draw(surface)
            if player.item_count("rabbits_foot") > 0:
                self.rabbit_btn.draw(surface)
            if player.item_count("marked_deck") > 0:
                self.deck_btn.draw(surface)
            if player.active_effects.get("guaranteed_win"):
                draw_text(surface, "Rabbit's Foot armed!", (170, C.INTERNAL_HEIGHT - 42), size=8, color=C.NEON_GREEN)
        elif self.phase == "player_turn":
            self.hit_btn.draw(surface)
            self.stand_btn.draw(surface)
            self.double_btn.enabled = len(self.player_hand) == 2 and player.chips >= self.bet
            self.double_btn.draw(surface)
        elif self.phase == "result":
            draw_text(surface, self.result_text, (C.INTERNAL_WIDTH // 2, C.INTERNAL_HEIGHT - 42), size=10,
                      color=self.result_color, center=True)
            self.play_again_btn.draw(surface)
            self.leave_btn.draw(surface)

        draw_text(surface, f"Chips: {player.chips}", (C.INTERNAL_WIDTH - 90, 4), size=9, color=C.GOLD)
