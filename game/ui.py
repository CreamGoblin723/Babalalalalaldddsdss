"""Reusable UI widgets: buttons, panels, text helpers."""
import pygame

from game import constants as C

_FONT_CACHE = {}


def get_font(size=14, bold=False):
    key = (size, bold)
    if key not in _FONT_CACHE:
        f = pygame.font.SysFont("dejavusansmono", size, bold=bold)
        _FONT_CACHE[key] = f
    return _FONT_CACHE[key]


def draw_text(surface, text, pos, size=14, color=C.UI_TEXT, bold=False, center=False, shadow=True):
    font = get_font(size, bold)
    if shadow:
        sh = font.render(text, True, (0, 0, 0))
        rect = sh.get_rect()
        if center:
            rect.center = (pos[0] + 1, pos[1] + 1)
        else:
            rect.topleft = (pos[0] + 1, pos[1] + 1)
        surface.blit(sh, rect)
    label = font.render(text, True, color)
    rect = label.get_rect()
    if center:
        rect.center = pos
    else:
        rect.topleft = pos
    surface.blit(label, rect)
    return rect


def draw_panel(surface, rect, bg=C.UI_PANEL, border=C.UI_BORDER, border_width=2):
    pygame.draw.rect(surface, bg, rect)
    pygame.draw.rect(surface, border, rect, border_width)
    # corner ticks for a bit of pixel-art flourish
    x, y, w, h = rect
    tick = min(6, w // 8, h // 8) or 2
    for (cx, cy) in [(x, y), (x + w - tick, y), (x, y + h - tick), (x + w - tick, y + h - tick)]:
        pygame.draw.rect(surface, border, (cx, cy, tick, tick))


def navigate_buttons(buttons, selected, event):
    """Generic Up/Down + Enter keyboard navigation for a vertical list of
    Buttons. Returns (new_selected_index, activated). Skips disabled
    buttons when moving the selection; does nothing if all are disabled."""
    if event.type != pygame.KEYDOWN or not buttons:
        return selected, False
    enabled_indices = [i for i, b in enumerate(buttons) if b.enabled]
    if not enabled_indices:
        return selected, False
    if event.key in (pygame.K_DOWN, pygame.K_s):
        pos = enabled_indices.index(selected) if selected in enabled_indices else -1
        return enabled_indices[(pos + 1) % len(enabled_indices)], False
    if event.key in (pygame.K_UP, pygame.K_w):
        pos = enabled_indices.index(selected) if selected in enabled_indices else 0
        return enabled_indices[(pos - 1) % len(enabled_indices)], False
    if event.key in (pygame.K_RETURN, pygame.K_SPACE):
        if selected in enabled_indices and buttons[selected].callback:
            buttons[selected].callback()
        return selected, True
    return selected, False


class Button:
    def __init__(self, rect, label, callback=None, size=14, enabled=True, hotkey=None):
        self.rect = pygame.Rect(rect)
        self.label = label
        self.callback = callback
        self.size = size
        self.hovered = False
        self.enabled = enabled
        self.hotkey = hotkey

    def handle_event(self, event):
        if not self.enabled:
            return False
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                if self.callback:
                    self.callback()
                return True
        elif event.type == pygame.KEYDOWN and self.hotkey is not None:
            if event.key == self.hotkey:
                if self.callback:
                    self.callback()
                return True
        return False

    def draw(self, surface):
        bg = C.UI_PANEL
        border = C.UI_BORDER
        text_color = C.UI_TEXT
        if not self.enabled:
            bg = (24, 22, 28)
            border = (70, 68, 74)
            text_color = C.UI_TEXT_DIM
        elif self.hovered:
            bg = (48, 32, 40)
            border = C.UI_SELECT
        draw_panel(surface, self.rect, bg=bg, border=border)
        draw_text(surface, self.label, self.rect.center, size=self.size, color=text_color, center=True)


class Slider:
    def __init__(self, rect, value=0.5, on_change=None):
        self.rect = pygame.Rect(rect)
        self.value = value
        self.on_change = on_change
        self.dragging = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.dragging = True
                self._update_from_mouse(event.pos[0])
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self._update_from_mouse(event.pos[0])

    def _update_from_mouse(self, mx):
        rel = (mx - self.rect.x) / max(1, self.rect.w)
        self.value = max(0.0, min(1.0, rel))
        if self.on_change:
            self.on_change(self.value)

    def draw(self, surface):
        pygame.draw.rect(surface, C.UI_PANEL, self.rect)
        pygame.draw.rect(surface, C.UI_BORDER, self.rect, 2)
        fill_w = int(self.rect.w * self.value)
        if fill_w > 0:
            pygame.draw.rect(surface, C.UI_SELECT, (self.rect.x, self.rect.y, fill_w, self.rect.h))
        knob_x = self.rect.x + fill_w
        pygame.draw.rect(surface, C.WHITE, (knob_x - 2, self.rect.y - 3, 4, self.rect.h + 6))
