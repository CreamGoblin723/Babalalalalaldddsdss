"""Regression test for the real mouse-click pipeline: pygame delivers
event.pos in actual window pixels, but every Button/Slider rect lives in
the low-res internal coordinate space that gets scaled up to fill the
window. GameApp must rescale event.pos before handing events to states,
or nothing is ever clickable in a real (non-headless) run."""
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame

from game import constants as C
from game.app import GameApp
from game.states.main_menu import MainMenuState
from game.states.character_select import CharacterSelectState

STATE_CLASSES = {
    "main_menu": MainMenuState,
    "character_select": CharacterSelectState,
}


def make_app():
    app = GameApp(STATE_CLASSES)
    app.push_state("main_menu")
    return app


def test_screen_space_click_hits_internal_space_button():
    app = make_app()
    menu = app.top
    new_game_btn = next(b for b in menu.buttons if b.label == "NEW GAME")

    # The button's rect lives in INTERNAL coordinates; simulate a real
    # click at the equivalent position in actual window (SCREEN) pixels,
    # exactly as pygame would deliver it from a real mouse.
    screen_w, screen_h = app.screen.get_size()
    ix, iy = new_game_btn.rect.center
    sx = ix * screen_w / C.INTERNAL_WIDTH
    sy = iy * screen_h / C.INTERNAL_HEIGHT

    pygame.event.post(pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=(sx, sy), button=1))
    pygame.event.post(pygame.event.Event(pygame.MOUSEBUTTONUP, pos=(sx, sy), button=1))
    app._handle_events()

    assert isinstance(app.top, CharacterSelectState), (
        "a screen-space click on NEW GAME should reach the button and push "
        "character_select; if this fails, mouse events aren't being "
        "rescaled into internal coordinates"
    )


def test_screen_space_click_outside_button_does_nothing():
    app = make_app()
    menu = app.top
    pygame.event.post(pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=(2, 2), button=1))
    pygame.event.post(pygame.event.Event(pygame.MOUSEBUTTONUP, pos=(2, 2), button=1))
    app._handle_events()
    assert app.top is menu


def test_translate_event_scales_mousemotion_pos():
    app = make_app()
    screen_w, screen_h = app.screen.get_size()
    ev = pygame.event.Event(pygame.MOUSEMOTION, pos=(screen_w, screen_h), rel=(0, 0), buttons=(0, 0, 0))
    translated = app._translate_event(ev)
    assert translated.pos[0] == C.INTERNAL_WIDTH
    assert translated.pos[1] == C.INTERNAL_HEIGHT


def test_translate_event_leaves_keydown_untouched():
    app = make_app()
    ev = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_DOWN, mod=0, unicode="")
    translated = app._translate_event(ev)
    assert translated is ev
