#!/usr/bin/env python3
"""Blood & Chips - a pixel-art top-down gambling roguelite.

Run with:  python3 main.py
"""
from game.app import GameApp
from game.states.main_menu import MainMenuState
from game.states.character_select import CharacterSelectState
from game.states.load_menu import LoadMenuState
from game.states.options import OptionsState
from game.states.overworld import OverworldState
from game.states.casino_interior import CasinoInteriorState
from game.states.shop import ShopState
from game.states.bar import BarState
from game.states.blackjack import BlackjackState
from game.states.coinflip import CoinFlipState
from game.states.overunder import OverUnderState
from game.states.slots import SlotsState
from game.states.roulette import RouletteState
from game.states.pause_menu import PauseMenuState
from game.states.run_end import RunEndState

STATE_CLASSES = {
    "main_menu": MainMenuState,
    "character_select": CharacterSelectState,
    "load_menu": LoadMenuState,
    "options": OptionsState,
    "overworld": OverworldState,
    "casino_interior": CasinoInteriorState,
    "shop": ShopState,
    "bar": BarState,
    "blackjack": BlackjackState,
    "coinflip": CoinFlipState,
    "overunder": OverUnderState,
    "slots": SlotsState,
    "roulette": RouletteState,
    "pause_menu": PauseMenuState,
    "run_end": RunEndState,
}


def main():
    app = GameApp(STATE_CLASSES)
    app.push_state("main_menu")
    app.run()


if __name__ == "__main__":
    main()
