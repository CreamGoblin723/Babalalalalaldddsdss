"""Pure slot-machine logic, kept separate from the pygame state so it can
be unit tested without a display."""
import random

SYMBOLS = ["cherry", "bell", "bar", "chip", "seven"]
BASE_WEIGHTS = {"cherry": 40, "bell": 25, "bar": 15, "chip": 12, "seven": 8}
PAYOUTS_3 = {"seven": 25, "bar": 10, "chip": 8, "bell": 5, "cherry": 3}
CHERRY_PAIR_PAYOUT = 2  # at least 2 cherries among the 3 reels - a modest real win, not just your stake back


def _weighted_symbol():
    return random.choices(list(BASE_WEIGHTS.keys()), weights=list(BASE_WEIGHTS.values()), k=1)[0]


def spin_reels(bias_strength: float = 0.0) -> tuple:
    """Spin 3 independent reels. bias_strength in [0, 1) is the Rigged
    Reels ability nudging the shoe: with that probability, reels 2 and 3
    each just copy reel 1's symbol instead of spinning independently,
    which raises the odds of a 3-of-a-kind without ever guaranteeing one."""
    r1 = _weighted_symbol()
    correlate_chance = min(0.6, max(0.0, bias_strength))
    r2 = r1 if random.random() < correlate_chance else _weighted_symbol()
    r3 = r1 if random.random() < correlate_chance else _weighted_symbol()
    return (r1, r2, r3)


def resolve_spin(reels: tuple) -> int:
    """Returns the payout multiplier for a spin result (0 = no win)."""
    r1, r2, r3 = reels
    if r1 == r2 == r3:
        return PAYOUTS_3.get(r1, 0)
    if sum(1 for r in reels if r == "cherry") >= 2:
        return CHERRY_PAIR_PAYOUT
    return 0
