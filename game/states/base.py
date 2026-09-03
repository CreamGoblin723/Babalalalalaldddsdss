"""Base class for all game states (screens)."""


class State:
    def __init__(self, app):
        self.app = app

    # lifecycle hooks -----------------------------------------------------
    def on_enter(self, **kwargs):
        pass

    def on_exit(self):
        pass

    def on_resume(self, **kwargs):
        """Called when a pushed state above this one is popped and control
        returns here. Default: same as on_enter with no args changed."""
        pass

    # per-frame ------------------------------------------------------------
    def handle_event(self, event):
        pass

    def update(self, dt):
        pass

    def draw(self, surface):
        pass
