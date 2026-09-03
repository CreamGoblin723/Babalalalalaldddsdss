import pygame

from game import constants as C
from game import save_manager
from game import game_flow
from game.states.base import State
from game.ui import Button, draw_text
from game.sprites import SKIN_NAMES


class LoadMenuState(State):
    def on_enter(self, **kwargs):
        self._build()

    def on_resume(self, **kwargs):
        self._build()

    def _build(self):
        self.slots = save_manager.list_slots()
        self.buttons = []
        w, h = 260, 50
        x = C.INTERNAL_WIDTH // 2 - w // 2
        y = 30
        gap = 56
        for s in self.slots:
            slot = s["slot"]
            self.buttons.append(("slot", s, Button((x, y, w, h), "", lambda sl=slot: self._select(sl))))
            if s["occupied"]:
                dx = x + w - 20
                self.buttons.append(("delete", s, Button((dx, y + 2, 18, 16), "X",
                                                           lambda sl=slot: self._delete(sl), size=10)))
            y += gap
        back_w = 100
        self.back_button = Button((C.INTERNAL_WIDTH // 2 - back_w // 2, y + 10, back_w, 20),
                                   "BACK", self._back)

    def _select(self, slot):
        s = self.slots[slot]
        if not s["occupied"]:
            return
        game_flow.resume_playthrough(self.app, slot)

    def _delete(self, slot):
        save_manager.delete_playthrough(slot)
        self._build()

    def _back(self):
        self.app.pop_state()

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self._back()
            return
        for kind, s, b in self.buttons:
            b.handle_event(event)
        self.back_button.handle_event(event)

    def draw(self, surface):
        surface.fill((16, 14, 22))
        draw_text(surface, "LOAD GAME", (C.INTERNAL_WIDTH // 2, 14), size=16, color=C.GOLD, center=True, bold=True)

        for kind, s, b in self.buttons:
            if kind != "slot":
                continue
            b.draw(surface)
            r = b.rect
            if s["occupied"]:
                skin_name = SKIN_NAMES.get(s.get("character", "drifter"), s.get("character", "?"))
                draw_text(surface, f"Slot {s['slot'] + 1}: {skin_name}", (r.x + 8, r.y + 6), size=11, color=C.UI_TEXT)
                draw_text(surface, f"Chips: {s['chips']}  |  {s.get('map_name', '')}",
                          (r.x + 8, r.y + 22), size=9, color=C.UI_TEXT_DIM)
            else:
                draw_text(surface, f"Slot {s['slot'] + 1}: empty", (r.x + 8, r.y + 18), size=11,
                          color=C.UI_TEXT_DIM)

        for kind, s, b in self.buttons:
            if kind == "delete":
                b.draw(surface)

        self.back_button.draw(surface)
