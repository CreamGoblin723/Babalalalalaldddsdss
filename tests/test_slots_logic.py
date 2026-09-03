import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import random

from game import slots_logic as slots


def test_three_of_a_kind_pays_its_symbol():
    assert slots.resolve_spin(("seven", "seven", "seven")) == slots.PAYOUTS_3["seven"]
    assert slots.resolve_spin(("bar", "bar", "bar")) == slots.PAYOUTS_3["bar"]


def test_two_cherries_pay_the_small_consolation():
    assert slots.resolve_spin(("cherry", "cherry", "bell")) == slots.CHERRY_PAIR_PAYOUT
    assert slots.resolve_spin(("cherry", "bar", "cherry")) == slots.CHERRY_PAIR_PAYOUT


def test_no_match_pays_nothing():
    assert slots.resolve_spin(("bell", "bar", "chip")) == 0


def test_spin_reels_returns_three_valid_symbols():
    random.seed(0)
    reels = slots.spin_reels(0.0)
    assert len(reels) == 3
    assert all(r in slots.SYMBOLS for r in reels)


def test_rigged_reels_bias_increases_three_of_a_kind_rate():
    random.seed(7)
    unbiased_hits = sum(1 for _ in range(3000) if len(set(slots.spin_reels(0.0))) == 1)
    random.seed(7)
    biased_hits = sum(1 for _ in range(3000) if len(set(slots.spin_reels(0.5))) == 1)
    assert biased_hits > unbiased_hits
