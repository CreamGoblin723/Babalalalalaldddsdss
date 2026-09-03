import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game.player import Player
from game import abilities


def test_biased_coin_without_ability_is_fair():
    p = Player()
    assert abilities.biased_coin(p) == 0.5


def test_biased_coin_with_lucky_coin_favors_player():
    p = Player()
    p.abilities.append("lucky_coin")
    assert abilities.biased_coin(p) > 0.5


def test_card_counter_reduction_only_with_ability():
    p = Player()
    assert abilities.card_counter_bust_reduction(p) == 0.0
    p.abilities.append("card_counter")
    assert abilities.card_counter_bust_reduction(p) > 0.0


def test_biased_die_favors_high_when_requested():
    import random
    p = Player()
    p.abilities.append("loaded_dice")
    random.seed(1)
    high_rolls = [abilities.draw_die(p, favor_high=True) for _ in range(2000)]
    random.seed(1)
    low_rolls = [abilities.draw_die(p, favor_high=False) for _ in range(2000)]
    assert sum(high_rolls) / len(high_rolls) > sum(low_rolls) / len(low_rolls)


def test_has_ability():
    p = Player()
    assert not p.has_ability("sharp_eyes")
    p.abilities.append("sharp_eyes")
    assert p.has_ability("sharp_eyes")


def test_has_effect_true_for_permanent_ability():
    p = Player()
    p.abilities.append("lucky_coin")
    assert p.has_effect("lucky_coin")


def test_has_effect_true_for_temporary_bar_buff():
    p = Player()
    assert not p.has_effect("lucky_coin")
    p.active_effects["temp_lucky_coin"] = True
    assert p.has_effect("lucky_coin")
    assert "lucky_coin" not in p.abilities  # still not permanently owned


def test_bias_helpers_honor_temporary_effects_too():
    p = Player()
    assert abilities.biased_coin(p) == 0.5
    p.active_effects["temp_lucky_coin"] = True
    assert abilities.biased_coin(p) > 0.5


def test_rigged_reels_bias():
    p = Player()
    assert abilities.rigged_reels_bias(p) == 0.0
    p.abilities.append("rigged_reels")
    assert abilities.rigged_reels_bias(p) > 0.0


def test_wheel_whisperer_bias():
    p = Player()
    assert abilities.wheel_whisperer_bias(p) == 0.0
    p.active_effects["temp_wheel_whisperer"] = True
    assert abilities.wheel_whisperer_bias(p) > 0.0
