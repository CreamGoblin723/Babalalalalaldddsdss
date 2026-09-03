"""The top-level Game application: window setup, the internal low-res
render surface, the main loop, and a simple state stack."""
import pygame

from game import constants as C
from game import save_manager, settings_manager


class GameApp:
    def __init__(self, state_classes: dict):
        pygame.init()
        try:
            pygame.mixer.init()
        except pygame.error:
            pass  # headless / no audio device available, that's fine

        self.settings = settings_manager.load_settings()
        self.screen = None
        self._render_rect = pygame.Rect(0, 0, C.SCREEN_WIDTH, C.SCREEN_HEIGHT)
        self._apply_display_mode()
        pygame.display.set_caption(C.TITLE)
        self.internal = pygame.Surface((C.INTERNAL_WIDTH, C.INTERNAL_HEIGHT))
        self.clock = pygame.time.Clock()

        self.state_classes = state_classes
        self.stack = []  # list of State instances
        self.running = True

        self.meta = save_manager.load_meta()
        self.player = None       # active Player during a playthrough
        self.active_slot = None  # which save slot the current playthrough uses

    # -- state stack --------------------------------------------------------
    def push_state(self, name, **kwargs):
        cls = self.state_classes[name]
        state = cls(self)
        self.stack.append(state)
        state.on_enter(**kwargs)

    def pop_state(self, **kwargs):
        if self.stack:
            state = self.stack.pop()
            state.on_exit()
        if self.stack:
            self.stack[-1].on_resume(**kwargs)

    def switch_state(self, name, **kwargs):
        """Replace the entire stack with a single new state."""
        while self.stack:
            self.stack.pop().on_exit()
        self.push_state(name, **kwargs)

    @property
    def top(self):
        return self.stack[-1] if self.stack else None

    # -- main loop ------------------------------------------------------
    def run(self):
        while self.running:
            dt = self.clock.tick(C.FPS) / 1000.0
            dt = min(dt, 0.05)  # clamp to avoid huge steps on hitches
            self._handle_events()
            if self.top:
                self.top.update(dt)
            self._draw()
        pygame.quit()

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                continue
            if event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
                self.toggle_fullscreen()
                continue
            if event.type == pygame.VIDEORESIZE:
                self._render_rect = self._compute_render_rect(self.screen.get_size())
                continue
            event = self._translate_event(event)
            if self.top:
                self.top.handle_event(event)

    def _translate_event(self, event):
        """Mouse events carry positions in real window pixels, but every
        Button/Slider rect is defined in the low-res internal coordinate
        space that gets letterboxed and scaled up to fill the window.
        Rescale event.pos into internal space (accounting for any
        letterbox/pillarbox offset) so clicks land on the right widget. A
        click that lands in the letterbox bars maps outside the internal
        canvas, so it simply misses everything, as it should."""
        if hasattr(event, "pos"):
            rect = self._render_rect
            rel_x = event.pos[0] - rect.x
            rel_y = event.pos[1] - rect.y
            x = rel_x * C.INTERNAL_WIDTH / rect.w if rect.w else -1
            y = rel_y * C.INTERNAL_HEIGHT / rect.h if rect.h else -1
            attrs = dict(event.dict)
            attrs["pos"] = (x, y)
            return pygame.event.Event(event.type, attrs)
        return event

    def _compute_render_rect(self, screen_size):
        """The largest rect of internal-aspect-ratio that fits centered in
        the current screen size, i.e. letterboxed (bars top/bottom) or
        pillarboxed (bars left/right) scaling that never distorts the art."""
        screen_w, screen_h = screen_size
        internal_aspect = C.INTERNAL_WIDTH / C.INTERNAL_HEIGHT
        if screen_w / max(1, screen_h) > internal_aspect:
            h = screen_h
            w = int(h * internal_aspect)
        else:
            w = screen_w
            h = int(w / internal_aspect)
        x = (screen_w - w) // 2
        y = (screen_h - h) // 2
        return pygame.Rect(x, y, max(1, w), max(1, h))

    def _draw(self):
        self.internal.fill(C.BLACK)
        for state in self.stack:
            state.draw(self.internal)
        self.screen.fill((0, 0, 0))
        scaled = pygame.transform.scale(self.internal, self._render_rect.size)
        self.screen.blit(scaled, self._render_rect.topleft)
        pygame.display.flip()

    def quit(self):
        self.running = False

    def toggle_fullscreen(self):
        self.settings["fullscreen"] = not self.settings.get("fullscreen", False)
        settings_manager.save_settings(self.settings)
        self.apply_video_settings()

    def apply_video_settings(self):
        self._apply_display_mode()

    def _apply_display_mode(self):
        if self.settings.get("fullscreen"):
            info = pygame.display.Info()
            size = (info.current_w, info.current_h)
            try:
                self.screen = pygame.display.set_mode(size, pygame.FULLSCREEN)
            except pygame.error:
                # some headless/virtual displays refuse a true fullscreen
                # mode switch; fall back to a plain window at that size
                self.screen = pygame.display.set_mode(size)
        else:
            self.screen = pygame.display.set_mode((C.SCREEN_WIDTH, C.SCREEN_HEIGHT), pygame.RESIZABLE)
        self._render_rect = self._compute_render_rect(self.screen.get_size())
