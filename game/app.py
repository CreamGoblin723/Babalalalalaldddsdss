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
        flags = pygame.FULLSCREEN if self.settings.get("fullscreen") else 0
        self.screen = pygame.display.set_mode((C.SCREEN_WIDTH, C.SCREEN_HEIGHT), flags)
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
            event = self._translate_event(event)
            if self.top:
                self.top.handle_event(event)

    def _translate_event(self, event):
        """Mouse events carry positions in real window pixels, but every
        Button/Slider rect is defined in the low-res internal coordinate
        space that gets scaled up to fill the window. Rescale event.pos
        into internal space so clicks actually land on the right widget."""
        if hasattr(event, "pos"):
            screen_w, screen_h = self.screen.get_size()
            x = event.pos[0] * C.INTERNAL_WIDTH / screen_w
            y = event.pos[1] * C.INTERNAL_HEIGHT / screen_h
            attrs = dict(event.dict)
            attrs["pos"] = (x, y)
            return pygame.event.Event(event.type, attrs)
        return event

    def _draw(self):
        self.internal.fill(C.BLACK)
        for state in self.stack:
            state.draw(self.internal)
        scaled = pygame.transform.scale(self.internal, (C.SCREEN_WIDTH, C.SCREEN_HEIGHT))
        self.screen.blit(scaled, (0, 0))
        pygame.display.flip()

    def quit(self):
        self.running = False

    def apply_video_settings(self):
        flags = pygame.FULLSCREEN if self.settings.get("fullscreen") else 0
        self.screen = pygame.display.set_mode((C.SCREEN_WIDTH, C.SCREEN_HEIGHT), flags)
