import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game.player import Player
from game import constants as C


def test_starting_chips():
    p = Player()
    assert p.chips == C.STARTING_CHIPS
    assert p.peak_chips == C.STARTING_CHIPS


def test_add_chips_tracks_peak():
    p = Player()
    p.add_chips(500)
    assert p.chips == C.STARTING_CHIPS + 500
    assert p.peak_chips == p.chips
    p.add_chips(-300)
    assert p.chips == C.STARTING_CHIPS + 200
    assert p.peak_chips == C.STARTING_CHIPS + 500  # peak stays at the high point


def test_bust_flag_on_zero_chips():
    p = Player()
    p.add_chips(-p.chips)
    assert p.chips == 0
    assert p.busted is True


def test_chips_never_go_negative():
    p = Player()
    p.add_chips(-999999)
    assert p.chips == 0


def test_win_flag_at_one_million():
    p = Player()
    p.add_chips(C.WIN_CHIPS)
    assert p.won_game is True


def test_inventory_add_use():
    p = Player()
    p.add_item("rabbits_foot", 2)
    assert p.item_count("rabbits_foot") == 2
    assert p.use_item("rabbits_foot") is True
    assert p.item_count("rabbits_foot") == 1
    assert p.use_item("rabbits_foot") is True
    assert p.item_count("rabbits_foot") == 0
    assert p.use_item("rabbits_foot") is False


def test_to_dict_from_dict_roundtrip():
    p = Player(name="X", skin="gold_baron")
    p.chips = 777
    p.abilities.append("sharp_eyes")
    p.add_item("marked_deck")
    d = p.to_dict()
    p2 = Player.from_dict(d)
    assert p2.name == "X"
    assert p2.skin == "gold_baron"
    assert p2.chips == 777
    assert p2.abilities == ["sharp_eyes"]
    assert p2.item_count("marked_deck") == 1


def test_blood_money_from_peak_monotonic():
    low = C.blood_money_from_peak(C.STARTING_CHIPS)
    mid = C.blood_money_from_peak(C.STARTING_CHIPS * 10)
    high = C.blood_money_from_peak(C.WIN_CHIPS)
    assert low <= mid <= high
    assert low >= 1
