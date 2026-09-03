"""Shared movement/collision logic for any free-roam top-down screen
(the outdoor overworld maps and the casino interior)."""
import pygame

from game import constants as C
from game.states.base import State
from game.sprites import get_character_sprite

PLAYER_HALF_W = 6
PLAYER_HALF_H = 5


class TopDownState(State):
    """Subclasses must set self.bounds (Rect) and self.obstacles (list of
    Rect) before update() is first called, and may override
    interact_zones() -> dict[name, Rect] and on_interact(name)."""

    bounds = None
    obstacles = ()

    def interact_zones(self):
        return {}

    def on_interact(self, name):
        pass

    def handle_topdown_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_e, pygame.K_RETURN, pygame.K_SPACE):
                if getattr(self, "prompt", None):
                    self.on_interact(self.prompt)
                return True
        return False

    def update_player(self, dt):
        player = self.app.player
        keys = pygame.key.get_pressed()
        dx = dy = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx -= 1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += 1
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy -= 1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy += 1

        moving = dx != 0 or dy != 0
        if moving:
            length = (dx ** 2 + dy ** 2) ** 0.5
            dx, dy = dx / length, dy / length
            if dx < 0:
                player.direction = "left"
            elif dx > 0:
                player.direction = "right"
            elif dy < 0:
                player.direction = "up"
            elif dy > 0:
                player.direction = "down"

            speed = C.PLAYER_SPEED
            new_x = player.x + dx * speed * dt
            new_y = player.y + dy * speed * dt
            if not self._collides(new_x, player.y):
                player.x = new_x
            if not self._collides(player.x, new_y):
                player.y = new_y

        player.update_walk_anim(dt, moving)
        self._update_prompt()

    def _player_rect(self, x, y):
        return pygame.Rect(x - PLAYER_HALF_W, y - PLAYER_HALF_H, PLAYER_HALF_W * 2, PLAYER_HALF_H * 2)

    def _collides(self, x, y):
        rect = self._player_rect(x, y)
        if self.bounds is not None and not self.bounds.contains(rect):
            return True
        for obs in self.obstacles:
            if rect.colliderect(obs):
                return True
        return False

    def _update_prompt(self):
        player = self.app.player
        prect = self._player_rect(player.x, player.y).inflate(10, 10)
        self.prompt = None
        for name, zone in self.interact_zones().items():
            if zone and prect.colliderect(zone):
                self.prompt = name
                break

    def draw_player(self, surface):
        player = self.app.player
        sprite = get_character_sprite(player.skin, player.direction, player.walk_frame, pixel_size=2)
        srect = sprite.get_rect(midbottom=(int(player.x), int(player.y) + PLAYER_HALF_H))
        surface.blit(sprite, srect)
