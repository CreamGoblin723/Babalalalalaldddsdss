import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game import blackjack_logic as bj


def test_hand_value_simple():
    assert bj.hand_value([("5", "S"), ("6", "H")]) == 11


def test_hand_value_face_cards():
    assert bj.hand_value([("K", "S"), ("Q", "H")]) == 20


def test_ace_soft_counts_as_eleven():
    assert bj.hand_value([("A", "S"), ("6", "H")]) == 17


def test_ace_reduces_when_busting():
    # A + 9 + 5 = 11 + 9 + 5 = 25 -> ace drops to 1 -> 15
    assert bj.hand_value([("A", "S"), ("9", "H"), ("5", "D")]) == 15


def test_multiple_aces():
    # A + A + 9 -> 11+11+9=31 -> reduce one ace -> 21
    assert bj.hand_value([("A", "S"), ("A", "H"), ("9", "D")]) == 21


def test_is_blackjack():
    assert bj.is_blackjack([("A", "S"), ("K", "H")])
    assert not bj.is_blackjack([("A", "S"), ("9", "H")])
    assert not bj.is_blackjack([("A", "S"), ("K", "H"), ("2", "D")])  # 3 cards, not a natural


def test_is_bust():
    assert bj.is_bust([("K", "S"), ("Q", "H"), ("5", "D")])
    assert not bj.is_bust([("K", "S"), ("Q", "H")])


def test_dealer_hits_below_17():
    assert bj.dealer_should_hit([("5", "S"), ("6", "H")])


def test_dealer_stands_hard_17():
    assert not bj.dealer_should_hit([("K", "S"), ("7", "H")])


def test_dealer_hits_soft_17():
    assert bj.dealer_should_hit([("A", "S"), ("6", "H")])


def test_dealer_stands_18_plus():
    assert not bj.dealer_should_hit([("K", "S"), ("8", "H")])


def test_draw_rank_bias_reduces_ten_value_frequency():
    import random
    random.seed(42)
    unbiased = [bj.rank_value(bj.draw_rank(0.0)) for _ in range(4000)]
    random.seed(42)
    biased = [bj.rank_value(bj.draw_rank(0.9)) for _ in range(4000)]
    unbiased_tens = sum(1 for v in unbiased if v == 10) / len(unbiased)
    biased_tens = sum(1 for v in biased if v == 10) / len(biased)
    assert biased_tens < unbiased_tens
