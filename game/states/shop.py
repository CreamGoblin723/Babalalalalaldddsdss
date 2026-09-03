import pygame

from game import constants as C
from game.states.base import State
from game.ui import Button, draw_text, draw_panel
from game.abilities import ABILITIES, ABILITY_ORDER
from game.shop_data import ITEMS, ITEM_ORDER


class ShopState(State):
    def on_enter(self, **kwargs):
        self.entries = []  # (kind, id)
        for aid in ABILITY_ORDER:
            self.entries.append(("ability", aid))
        for iid in ITEM_ORDER:
            self.entries.append(("item", iid))
        self.selected = 0
        self.message = ""
        self.message_timer = 0.0
        self._build_rows()
        self.back_btn = Button((C.INTERNAL_WIDTH - 66, C.INTERNAL_HEIGHT - 20, 58, 15), "LEAVE", self._leave, size=9)

    def _build_rows(self):
        self.row_rects = []
        self.buy_buttons = []
        y = 24
        row_h = 12
        for i, (kind, key) in enumerate(self.entries):
            rect = pygame.Rect(6, y, C.INTERNAL_WIDTH - 12, row_h - 1)
            self.row_rects.append(rect)
            btn = Button((rect.right - 30, rect.y, 28, rect.h), "BUY", (lambda i=i: self._buy(i)), size=8)
            self.buy_buttons.append(btn)
            y += row_h

    def _leave(self):
        self.app.pop_state()

    def _info(self, kind, key):
        if kind == "ability":
            return ABILITIES[key]
        return ITEMS[key]

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

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self._leave()
                return
            if event.key in (pygame.K_UP, pygame.K_w):
                self.selected = max(0, self.selected - 1)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.selected = min(len(self.entries) - 1, self.selected + 1)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self._buy(self.selected)
        for i, btn in enumerate(self.buy_buttons):
            btn.handle_event(event)
        self.back_btn.handle_event(event)
        if event.type == pygame.MOUSEMOTION:
            for i, rect in enumerate(self.row_rects):
                if rect.collidepoint(event.pos):
                    self.selected = i

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

        for i, (kind, key) in enumerate(self.entries):
            rect = self.row_rects[i]
            info = self._info(kind, key)
            owned = kind == "ability" and player.has_ability(key)
            selected = i == self.selected
            bg = (40, 30, 44) if selected else (24, 20, 28)
            pygame.draw.rect(surface, bg, rect)
            if selected:
                pygame.draw.rect(surface, C.UI_SELECT, rect, 1)
            tag = "[Ability]" if kind == "ability" else "[Item]"
            name = info["name"]
            draw_text(surface, f"{name}", (rect.x + 3, rect.y + 3), size=8,
                      color=C.UI_TEXT_DIM if owned else C.UI_TEXT)
            if owned:
                draw_text(surface, "OWNED", (rect.right - 34, rect.y + 3), size=8, color=C.NEON_GREEN)
            else:
                afford = player.can_afford(info["cost"])
                draw_text(surface, f"{info['cost']}c", (rect.right - 60, rect.y + 3), size=8,
                          color=C.GOLD if afford else C.UI_TEXT_DIM)
                self.buy_buttons[i].enabled = afford
                self.buy_buttons[i].draw(surface)

        desc_panel = pygame.Rect(6, C.INTERNAL_HEIGHT - 46, C.INTERNAL_WIDTH - 12, 22)
        draw_panel(surface, desc_panel, bg=(20, 18, 26))
        if self.message:
            draw_text(surface, self.message, desc_panel.center, size=8, color=C.GOLD, center=True)
        elif 0 <= self.selected < len(self.entries):
            kind, key = self.entries[self.selected]
            info = self._info(kind, key)
            draw_text(surface, info["desc"], (desc_panel.x + 4, desc_panel.y + 6), size=7, color=C.UI_TEXT_DIM)

        draw_text(surface, f"Chips: {player.chips}", (6, C.INTERNAL_HEIGHT - 12), size=9, color=C.GOLD)
        self.back_btn.draw(surface)
