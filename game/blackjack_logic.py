"""Pure blackjack rules/logic, kept separate from the pygame state so it can
be unit tested without a display."""
import random

RANKS = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
SUITS = ["S", "H", "D", "C"]


def rank_value(rank: str) -> int:
    if rank == "A":
        return 11
    if rank in ("10", "J", "Q", "K"):
        return 10
    return int(rank)


def draw_rank(bias_reduce_high: float = 0.0) -> str:
    """Draw a random rank. bias_reduce_high in [0,1) shifts probability mass
    away from the ten-value ranks (10/J/Q/K), used by the Card Counter
    ability to quietly lower the player's bust risk."""
    weights = []
    for r in RANKS:
        w = 1.0
        if bias_reduce_high and rank_value(r) == 10:
            w *= max(0.05, 1.0 - bias_reduce_high)
        weights.append(w)
    return random.choices(RANKS, weights=weights, k=1)[0]


def draw_card(bias_reduce_high: float = 0.0) -> tuple:
    return (draw_rank(bias_reduce_high), random.choice(SUITS))


def hand_value(cards: list) -> int:
    """cards: list of (rank, suit). Returns best value <=21 if possible
    (soft aces counted down as needed)."""
    total = sum(rank_value(r) for r, _ in cards)
    aces = sum(1 for r, _ in cards if r == "A")
    while total > 21 and aces > 0:
        total -= 10
        aces -= 1
    return total


def is_blackjack(cards: list) -> bool:
    return len(cards) == 2 and hand_value(cards) == 21


def is_bust(cards: list) -> bool:
    return hand_value(cards) > 21


def dealer_should_hit(cards: list, stand_on_soft_17=False) -> bool:
    value = hand_value(cards)
    if value < 17:
        return True
    if value == 17 and not stand_on_soft_17:
        # check for soft 17 (an ace still counted as 11)
        total_raw = sum(rank_value(r) for r, _ in cards)
        aces = sum(1 for r, _ in cards if r == "A")
        reduced = 0
        t = total_raw
        while t > 21 and aces > reduced:
            t -= 10
            reduced += 1
        is_soft = aces > reduced and t == 17
        return is_soft
    return False
