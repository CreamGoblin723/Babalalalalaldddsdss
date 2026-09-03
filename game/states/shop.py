import pygame

from game import constants as C
from game.states.base import State
from game.ui import Button, draw_text, draw_panel, get_font, wrap_text
from game.abilities import ABILITIES, ABILITY_ORDER
from game.shop_data import ITEMS, ITEM_ORDER

VISIBLE_ROWS = 11
ROW_H = 12
LIST_TOP = 22
DESC_PANEL = pygame.Rect(6, LIST_TOP + VISIBLE_ROWS * ROW_H + 3, C.INTERNAL_WIDTH - 12, 32)


class ShopState(State):
    def on_enter(self, **kwargs):
        self.entries = []  # (kind, id)
        for aid in ABILITY_ORDER:
            self.entries.append(("ability", aid))
        for iid in ITEM_ORDER:
            self.entries.append(("item", iid))
        self.selected = 0
        self.scroll = 0
        self.message = ""
        self.message_timer = 0.0
        self._build_rows()
        self.back_btn = Button((C.INTERNAL_WIDTH - 66, C.INTERNAL_HEIGHT - 20, 58, 15), "LEAVE", self._leave, size=9)

    def _build_rows(self):
        self.row_rects = []
        self.buy_buttons = []
        y = LIST_TOP
        for slot in range(VISIBLE_ROWS):
            rect = pygame.Rect(6, y, C.INTERNAL_WIDTH - 12, ROW_H - 1)
            self.row_rects.append(rect)
            btn = Button((rect.right - 30, rect.y, 28, rect.h), "BUY", (lambda s=slot: self._buy_slot(s)), size=8)
            self.buy_buttons.append(btn)
            y += ROW_H

    def _leave(self):
        self.app.pop_state()

    def _info(self, kind, key):
        if kind == "ability":
            return ABILITIES[key]
        return ITEMS[key]

    def _buy_slot(self, slot):
        index = self.scroll + slot
        if 0 <= index < len(self.entries):
            self._buy(index)

    def _buy(self, index):
        kind, key = self.entries[index]
        player = self.app.player
        info = self._info(kind, key)
        cost = info["cost"]
        if kind == "ability" and player.has_ability(key):
            self._flash("Already own that.")
            return
        if not player.can_afford(cost):
            self._flash("Not enough chips.")
            return
        player.add_chips(-cost)
        if kind == "ability":
            player.abilities.append(key)
            self._flash(f"Bought {info['name']}!")
        else:
            player.add_item(key)
            self._flash(f"Bought {info['name']}!")

    def _flash(self, msg):
        self.message = msg
        self.message_timer = 1.4

    def _ensure_visible(self):
        if self.selected < self.scroll:
            self.scroll = self.selected
        elif self.selected >= self.scroll + VISIBLE_ROWS:
            self.scroll = self.selected - VISIBLE_ROWS + 1
        self.scroll = max(0, min(self.scroll, max(0, len(self.entries) - VISIBLE_ROWS)))

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self._leave()
                return
            if event.key in (pygame.K_UP, pygame.K_w):
                self.selected = max(0, self.selected - 1)
                self._ensure_visible()
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.selected = min(len(self.entries) - 1, self.selected + 1)
                self._ensure_visible()
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self._buy(self.selected)
        for btn in self.buy_buttons:
            btn.handle_event(event)
        self.back_btn.handle_event(event)
        if event.type == pygame.MOUSEWHEEL:
            self.scroll = max(0, min(self.scroll - event.y, max(0, len(self.entries) - VISIBLE_ROWS)))
        if event.type == pygame.MOUSEMOTION:
            for slot, rect in enumerate(self.row_rects):
                index = self.scroll + slot
                if index < len(self.entries) and rect.collidepoint(event.pos):
                    self.selected = index

    def update(self, dt):
        if self.message_timer > 0:
            self.message_timer -= dt
            if self.message_timer <= 0:
                self.message = ""

    def draw(self, surface):
        surface.fill((14, 12, 18))
        draw_text(surface, "THE SHADY MAN", (C.INTERNAL_WIDTH // 2, 6), size=13, color=C.BLOOD_RED,
                  center=True, bold=True)
        player = self.app.player

        for slot in range(VISIBLE_ROWS):
            index = self.scroll + slot
            rect = self.row_rects[slot]
            self.buy_buttons[slot].enabled = False
            if index >= len(self.entries):
                continue
            kind, key = self.entries[index]
            info = self._info(kind, key)
            owned = kind == "ability" and player.has_ability(key)
            selected = index == self.selected
            bg = (40, 30, 44) if selected else (24, 20, 28)
            pygame.draw.rect(surface, bg, rect)
            if selected:
                pygame.draw.rect(surface, C.UI_SELECT, rect, 1)
            draw_text(surface, info["name"], (rect.x + 3, rect.y + 3), size=8,
                      color=C.UI_TEXT_DIM if owned else C.UI_TEXT)
            if owned:
                draw_text(surface, "OWNED", (rect.right - 34, rect.y + 3), size=8, color=C.NEON_GREEN)
            else:
                afford = player.can_afford(info["cost"])
                draw_text(surface, f"{info['cost']}c", (rect.right - 60, rect.y + 3), size=8,
                          color=C.GOLD if afford else C.UI_TEXT_DIM)
                self.buy_buttons[slot].enabled = afford
                self.buy_buttons[slot].draw(surface)

        if len(self.entries) > VISIBLE_ROWS:
            label = (f"{self.scroll + 1}-{min(len(self.entries), self.scroll + VISIBLE_ROWS)} "
                     f"of {len(self.entries)}")
            width = get_font(7).size(label)[0]
            draw_text(surface, label, (C.INTERNAL_WIDTH - 8 - width, 7), size=7, color=C.UI_TEXT_DIM)

        desc_panel = DESC_PANEL
        draw_panel(surface, desc_panel, bg=(20, 18, 26))
        if self.message:
            draw_text(surface, self.message, desc_panel.center, size=8, color=C.GOLD, center=True)
        elif 0 <= self.selected < len(self.entries):
            kind, key = self.entries[self.selected]
            info = self._info(kind, key)
            lines = wrap_text(info["desc"], size=7, max_width=desc_panel.w - 8)
            for i, line in enumerate(lines[:2]):
                draw_text(surface, line, (desc_panel.x + 4, desc_panel.y + 4 + i * 10), size=7,
                          color=C.UI_TEXT_DIM)

        draw_text(surface, f"Chips: {player.chips}", (6, C.INTERNAL_HEIGHT - 12), size=9, color=C.GOLD)
        self.back_btn.draw(surface)
