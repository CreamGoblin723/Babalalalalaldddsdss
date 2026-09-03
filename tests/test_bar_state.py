import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame

from game.app import GameApp
from game.states.bar import BarState
from game.player import Player
from game.bar_data import DRINKS, DRINK_ORDER

pygame.init()


def make_app_with_player():
    app = GameApp({"bar": BarState})
    app.player = Player()
    app.player.chips = 1000
    app.push_state("bar")
    return app


def test_buying_a_drink_charges_chips_and_grants_temp_effect():
    app = make_app_with_player()
    bar = app.top
    starting_chips = app.player.chips
    drink_id = DRINK_ORDER[0]
    drink = DRINKS[drink_id]

    bar._buy(0)

    assert app.player.chips == starting_chips - drink["cost"]
    assert app.player.active_effects.get(f"temp_{drink['grants']}") is True


def test_buying_without_enough_chips_flashes_and_charges_nothing():
    app = make_app_with_player()
    bar = app.top
    app.player.chips = 0

    bar._buy(0)

    assert app.player.chips == 0
    assert bar.message  # some "not enough chips" message shown
