#!/usr/bin/env python3
"""Headless smoke test: drives the whole game through every screen and both
minigame outcomes using synthetic pygame events, to catch crashes that
only show up once the app is actually running (as opposed to just
importing cleanly)."""
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame

from game.app import GameApp
from game.states.main_menu import MainMenuState
from game.states.character_select import CharacterSelectState
from game.states.load_menu import LoadMenuState
from game.states.options import OptionsState
from game.states.overworld import OverworldState
from game.states.casino_interior import CasinoInteriorState
from game.states.shop import ShopState
from game.states.blackjack import BlackjackState
from game.states.coinflip import CoinFlipState
from game.states.overunder import OverUnderState
from game.states.pause_menu import PauseMenuState
from game.states.run_end import RunEndState
from game import save_manager

STATE_CLASSES = {
    "main_menu": MainMenuState,
    "character_select": CharacterSelectState,
    "load_menu": LoadMenuState,
    "options": OptionsState,
    "overworld": OverworldState,
    "casino_interior": CasinoInteriorState,
    "shop": ShopState,
    "blackjack": BlackjackState,
    "coinflip": CoinFlipState,
    "overunder": OverUnderState,
    "pause_menu": PauseMenuState,
    "run_end": RunEndState,
}


def tick(app, n=3, dt=0.016):
    for _ in range(n):
        if app.top:
            app.top.update(dt)
        app._draw()


def key(app, k, unicode=""):
    ev = pygame.event.Event(pygame.KEYDOWN, key=k, unicode=unicode, mod=0)
    if app.top:
        app.top.handle_event(ev)
    ev_up = pygame.event.Event(pygame.KEYUP, key=k, mod=0)
    if app.top:
        app.top.handle_event(ev_up)


def click(app, pos):
    down = pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=pos, button=1)
    if app.top:
        app.top.handle_event(down)
    up = pygame.event.Event(pygame.MOUSEBUTTONUP, pos=pos, button=1)
    if app.top:
        app.top.handle_event(up)


def main():
    # clean slate
    for f in ["meta.json", "settings.json", "slot_0.json", "slot_1.json", "slot_2.json"]:
        from game import constants as C
        p = os.path.join(C.SAVES_DIR, f)
        if os.path.exists(p):
            os.remove(p)

    app = GameApp(STATE_CLASSES)
    app.push_state("main_menu")
    assert isinstance(app.top, MainMenuState)
    tick(app)
    print("OK: main menu")

    # Options screen
    app.push_state("options")
    tick(app)
    app.pop_state()
    print("OK: options")

    # Load menu (empty)
    app.push_state("load_menu")
    tick(app)
    app.pop_state()
    print("OK: load menu (empty)")

    # New game -> character select
    app.push_state("character_select")
    cs = app.top
    assert isinstance(cs, CharacterSelectState)
    cs.name = "Tester"
    cs._next_skin()
    cs._prev_skin()
    tick(app)
    cs._start()
    assert isinstance(app.top, OverworldState)
    print("OK: character select -> overworld (home)")

    ow = app.top
    assert app.player is not None
    assert app.player.chips == 500

    # Walk toward the van and enter it (home -> casino_area)
    van = ow.map["van"]
    app.player.x, app.player.y = van.centerx, van.centery
    tick(app)
    key(app, pygame.K_e)
    assert app.player.map_name == "casino_area"
    print("OK: van transition home -> casino_area")

    ow = app.top
    # Walk to shady man and open the shop
    shady = ow.map["shady_man"]
    app.player.x, app.player.y = shady.centerx, shady.centery
    tick(app)
    key(app, pygame.K_e)
    assert isinstance(app.top, ShopState)
    print("OK: shop opened")

    shop = app.top
    app.player.chips = 5000
    shop._buy(0)  # buy first ability
    assert len(app.player.abilities) >= 1
    tick(app)
    app.pop_state()
    assert isinstance(app.top, OverworldState)
    print("OK: bought ability, back to overworld")

    ow = app.top
    door = ow.map["casino_door"]
    app.player.x, app.player.y = door.centerx, door.centery
    tick(app)
    key(app, pygame.K_e)
    assert isinstance(app.top, CasinoInteriorState)
    print("OK: entered casino interior")

    ci = app.top
    from game.states.casino_interior import TABLES
    bj_pos = TABLES["blackjack"]["pos"]
    app.player.x, app.player.y = bj_pos
    tick(app)
    key(app, pygame.K_e)
    assert isinstance(app.top, BlackjackState)
    print("OK: blackjack table opened")

    bjstate = app.top
    app.player.chips = 1000
    bjstate.bet = 50
    bjstate._deal()
    tick(app)
    # play until result, hitting is safe since we just want to exercise code paths
    guard = 0
    while bjstate.phase == "player_turn" and guard < 20:
        bjstate._stand()
        guard += 1
    tick(app)
    assert bjstate.phase in ("result",)
    print("OK: blackjack hand resolved:", bjstate.result_text)
    bjstate._reset_for_bet()
    app.pop_state()
    assert isinstance(app.top, CasinoInteriorState)
    print("OK: left blackjack table")

    cf_pos = TABLES["coinflip"]["pos"]
    app.player.x, app.player.y = cf_pos
    tick(app)
    key(app, pygame.K_e)
    assert isinstance(app.top, CoinFlipState)
    cfstate = app.top
    cfstate.bet = 20
    cfstate._flip()
    guard = 0
    while cfstate.phase == "flipping" and guard < 200:
        cfstate.update(0.05)
        guard += 1
    assert cfstate.phase == "result"
    print("OK: coinflip resolved:", cfstate.result_text)
    app.pop_state()

    ou_pos = TABLES["overunder"]["pos"]
    app.player.x, app.player.y = ou_pos
    tick(app)
    key(app, pygame.K_e)
    assert isinstance(app.top, OverUnderState)
    oustate = app.top
    oustate.bet = 20
    oustate.choice = "over"
    oustate._roll()
    guard = 0
    while oustate.phase == "rolling" and guard < 200:
        oustate.update(0.05)
        guard += 1
    assert oustate.phase == "result"
    print("OK: over/under resolved:", oustate.result_text)
    app.pop_state()

    assert isinstance(app.top, CasinoInteriorState)
    app.pop_state()
    assert isinstance(app.top, OverworldState)
    print("OK: back at casino_area overworld")

    # Pause menu + save
    key(app, pygame.K_ESCAPE)
    assert isinstance(app.top, PauseMenuState)
    pm = app.top
    pm._save()
    tick(app)
    pm._resume()
    print("OK: pause menu save/resume")

    slots = save_manager.list_slots()
    assert any(s["occupied"] for s in slots), "expected a save slot to be occupied"
    print("OK: save slot persisted:", [s for s in slots if s["occupied"]])

    # Force a win to exercise run_end (victory)
    app.player.chips = 999_999
    from game import game_flow
    app.player.add_chips(5000)
    ended = game_flow.check_run_end(app)
    assert ended
    assert isinstance(app.top, RunEndState)
    tick(app)
    print("OK: victory run_end screen:", app.top.result_text if hasattr(app.top, "result_text") else "shown")
    app.top._to_menu()
    assert isinstance(app.top, MainMenuState)
    print("OK: returned to main menu after victory")

    # Bankrupt path
    app.push_state("character_select")
    cs = app.top
    cs.name = "Buster"
    cs._start()
    assert isinstance(app.top, OverworldState)
    app.player.add_chips(-app.player.chips)
    ended = game_flow.check_run_end(app)
    assert ended
    assert isinstance(app.top, RunEndState)
    print("OK: bankrupt run_end screen")
    app.top._to_menu()

    meta = save_manager.load_meta()
    print("OK: final Blood Money total:", meta.get("blood_money"))
    assert meta.get("blood_money", 0) > 0

    print("\nALL SMOKE TESTS PASSED")


if __name__ == "__main__":
    main()
