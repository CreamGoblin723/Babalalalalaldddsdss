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
    # click the bottom-right corner of the actual rendered (possibly
    # letterboxed) rect, not the raw screen - that corner must map to
    # exactly the internal canvas's bottom-right corner.
    rect = app._render_rect
    ev = pygame.event.Event(pygame.MOUSEMOTION, pos=(rect.right, rect.bottom), rel=(0, 0), buttons=(0, 0, 0))
    translated = app._translate_event(ev)
    assert round(translated.pos[0]) == C.INTERNAL_WIDTH
    assert round(translated.pos[1]) == C.INTERNAL_HEIGHT


def test_translate_event_leaves_keydown_untouched():
    app = make_app()
    ev = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_DOWN, mod=0, unicode="")
    translated = app._translate_event(ev)
    assert translated is ev


def test_render_rect_pillarboxes_a_wide_screen():
    """An ultrawide window is wider than the internal aspect ratio, so bars
    must appear on the left/right (pillarboxing), full height used."""
    app = make_app()
    rect = app._compute_render_rect((2560, 1080))
    assert rect.h == 1080
    assert rect.w < 2560
    assert rect.x > 0
    assert abs((rect.x * 2) + rect.w - 2560) <= 1  # centered


def test_render_rect_letterboxes_a_tall_screen():
    """A narrow/tall window is narrower than the internal aspect ratio, so
    bars must appear on the top/bottom (letterboxing), full width used."""
    app = make_app()
    rect = app._compute_render_rect((800, 1200))
    assert rect.w == 800
    assert rect.h < 1200
    assert rect.y > 0
    assert abs((rect.y * 2) + rect.h - 1200) <= 1  # centered


def test_click_in_letterbox_bar_hits_nothing():
    """A click that lands in the black bar (outside the rendered rect)
    should map outside the internal canvas, not get clamped onto an edge
    widget."""
    app = make_app()
    app._render_rect = app._compute_render_rect((800, 1200))  # force letterboxing
    ev = pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=(400, 5), button=1)  # top bar
    translated = app._translate_event(ev)
    assert translated.pos[1] < 0


def test_f11_toggles_fullscreen_setting():
    app = make_app()
    before = app.settings.get("fullscreen", False)
    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_F11, mod=0, unicode=""))
    app._handle_events()
    assert app.settings.get("fullscreen") != before
    # toggle back so we don't leave the test suite in fullscreen
    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_F11, mod=0, unicode=""))
    app._handle_events()
    assert app.settings.get("fullscreen") == before
