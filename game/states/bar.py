import pygame

from game import constants as C
from game.states.base import State
from game.ui import Button, draw_text, draw_panel
from game.bar_data import DRINKS, DRINK_ORDER
from game.abilities import ABILITIES


class BarState(State):
    def on_enter(self, **kwargs):
        self.selected = 0
        self.message = ""
        self.message_timer = 0.0
        self._build_rows()
        self.back_btn = Button((C.INTERNAL_WIDTH - 66, C.INTERNAL_HEIGHT - 20, 58, 15), "LEAVE", self._leave, size=9)

    def _build_rows(self):
        self.row_rects = []
        self.buy_buttons = []
        y = 34
        row_h = 26
        for i, drink_id in enumerate(DRINK_ORDER):
            rect = pygame.Rect(6, y, C.INTERNAL_WIDTH - 12, row_h - 3)
            self.row_rects.append(rect)
            btn = Button((rect.right - 34, rect.y + 4, 30, 16), "ORDER", (lambda i=i: self._buy(i)), size=7)
            self.buy_buttons.append(btn)
            y += row_h

    def _leave(self):
        self.app.pop_state()

    def _buy(self, index):
        player = self.app.player
        drink_id = DRINK_ORDER[index]
        drink = DRINKS[drink_id]
        cost = drink["cost"]
        if not player.can_afford(cost):
            self._flash("Not enough chips.")
            return
        player.add_chips(-cost)
        player.active_effects[f"temp_{drink['grants']}"] = True
        self._flash(f"{drink['name']} — feeling lucky.")

    def _flash(self, msg):
        self.message = msg
        self.message_timer = 1.6

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self._leave()
                return
            if event.key in (pygame.K_UP, pygame.K_w):
                self.selected = max(0, self.selected - 1)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.selected = min(len(DRINK_ORDER) - 1, self.selected + 1)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self._buy(self.selected)
        for btn in self.buy_buttons:
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
        surface.fill((26, 18, 14))
        draw_text(surface, "THE BACK BAR", (C.INTERNAL_WIDTH // 2, 6), size=13, color=C.GOLD,
                  center=True, bold=True)
        draw_text(surface, "cheap, temporary luck - wears off when you leave The Strip",
                  (C.INTERNAL_WIDTH // 2, 20), size=7, color=C.UI_TEXT_DIM, center=True)

        player = self.app.player
        for i, drink_id in enumerate(DRINK_ORDER):
            drink = DRINKS[drink_id]
            rect = self.row_rects[i]
            selected = i == self.selected
            active = bool(player.active_effects.get(f"temp_{drink['grants']}"))
            bg = (54, 34, 22) if selected else (36, 22, 16)
            pygame.draw.rect(surface, bg, rect)
            if selected:
                pygame.draw.rect(surface, C.UI_SELECT, rect, 1)
            draw_text(surface, drink["name"], (rect.x + 4, rect.y + 3), size=9, color=C.UI_TEXT)
            ability_name = ABILITIES[drink["grants"]]["name"]
            tag = "ACTIVE" if active else f"grants temp. {ability_name}"
            draw_text(surface, tag, (rect.x + 4, rect.y + 14), size=6,
                      color=C.NEON_GREEN if active else C.UI_TEXT_DIM)
            afford = player.can_afford(drink["cost"])
            draw_text(surface, f"{drink['cost']}c", (rect.right - 70, rect.y + 8), size=8,
                      color=C.GOLD if afford else C.UI_TEXT_DIM)
            self.buy_buttons[i].enabled = afford
            self.buy_buttons[i].draw(surface)

        desc_panel = pygame.Rect(6, C.INTERNAL_HEIGHT - 46, C.INTERNAL_WIDTH - 12, 22)
        draw_panel(surface, desc_panel, bg=(20, 14, 12))
        if self.message:
            draw_text(surface, self.message, desc_panel.center, size=8, color=C.GOLD, center=True)
        else:
            drink = DRINKS[DRINK_ORDER[self.selected]]
            draw_text(surface, drink["desc"], (desc_panel.x + 4, desc_panel.y + 6), size=7, color=C.UI_TEXT_DIM)

        draw_text(surface, f"Chips: {player.chips}", (6, C.INTERNAL_HEIGHT - 12), size=9, color=C.GOLD)
        self.back_btn.draw(surface)
