import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import random

from game import roulette_logic as roulette


def test_number_color_zero_is_green():
    assert roulette.number_color(0) == "green"


def test_number_color_red_black_partition_covers_1_to_36():
    for n in range(1, 37):
        color = roulette.number_color(n)
        assert color in ("red", "black")
    assert len(roulette.RED_NUMBERS) == 18


def test_bet_wins_red_black():
    red_number = next(iter(roulette.RED_NUMBERS))
    black_number = next(n for n in range(1, 37) if n not in roulette.RED_NUMBERS)
    assert roulette.bet_wins("red", red_number)
    assert not roulette.bet_wins("black", red_number)
    assert roulette.bet_wins("black", black_number)


def test_bet_wins_odd_even_zero_is_neither():
    assert roulette.bet_wins("odd", 1)
    assert roulette.bet_wins("even", 2)
    assert not roulette.bet_wins("odd", 0)
    assert not roulette.bet_wins("even", 0)


def test_bet_wins_low_high():
    assert roulette.bet_wins("low", 1)
    assert roulette.bet_wins("low", 18)
    assert not roulette.bet_wins("low", 19)
    assert roulette.bet_wins("high", 19)
    assert roulette.bet_wins("high", 36)


def test_bet_wins_green():
    assert roulette.bet_wins("green", 0)
    assert not roulette.bet_wins("green", 1)


def test_spin_without_bias_returns_valid_number():
    random.seed(1)
    for _ in range(50):
        n = roulette.spin()
        assert 0 <= n <= 36


def test_wheel_whisperer_bias_increases_win_rate():
    random.seed(3)
    unbiased_wins = sum(1 for _ in range(4000) if roulette.bet_wins("red", roulette.spin("red", 0.0)))
    random.seed(3)
    biased_wins = sum(1 for _ in range(4000) if roulette.bet_wins("red", roulette.spin("red", 0.5)))
    assert biased_wins > unbiased_wins
