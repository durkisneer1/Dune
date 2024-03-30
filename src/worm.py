from typing import TYPE_CHECKING

import pygame as pg

from src.core.settings import *

if TYPE_CHECKING:
    from main import Game


class Worm:
    def __init__(self, game: "Game"):
        self.game = game
        self.colliders = [tile.rect for tile in game.collision_tiles]

        self.head = BodySegment()
        self.head.pos.xy = WORLD_WIDTH / 2, WORLD_HEIGHT / 2
        self.head_rect = pg.Rect(self.head.pos, (10, 10))
        self.segments = []
        for i in range(10):
            segment = BodySegment(
                self.head if i == 0 else self.segments[i - 1],
                (255 - i * 20, 255 - i * 20, 255 - i * 20)
            )
            self.segments.append(segment)
        self.segments.reverse()

        self.direction = pg.Vector2(1, 0)
        self.speed = 100

    def update(self):
        if self.game.keys[pg.K_LEFT]:
            self.direction.rotate_ip(-self.game.dt * 115)
        if self.game.keys[pg.K_RIGHT]:
            self.direction.rotate_ip(self.game.dt * 115)
        self.direction.normalize_ip()

        velocity = self.direction * self.speed * self.game.dt
        self.head.pos.x += velocity.x
        self.h_collide()
        self.head.pos.y += velocity.y
        self.v_collide()

        for segment in self.segments:
            segment.update()

        self.game.camera = self.game.camera.lerp(
            self.head.pos - pg.Vector2(WIN_WIDTH / 2, WIN_HEIGHT / 2),
            self.game.dt * 10
        )

    def h_collide(self):
        self.head_rect.centerx = self.head.pos.x
        for collider in self.colliders:
            if self.head_rect.colliderect(collider):
                if self.direction.x > 0:
                    self.head_rect.right = collider.left
                elif self.direction.x < 0:
                    self.head_rect.left = collider.right
                self.head.pos.x = self.head_rect.centerx

    def v_collide(self):
        self.head_rect.centery = self.head.pos.y
        for collider in self.colliders:
            if self.head_rect.colliderect(collider):
                if self.direction.y > 0:
                    self.head_rect.bottom = collider.top
                elif self.direction.y < 0:
                    self.head_rect.top = collider.bottom
                self.head.pos.y = self.head_rect.centery

    def draw(self):
        for segment in self.segments:
            pg.draw.circle(self.game.screen, segment.color, segment.pos - self.game.camera, 8)


class BodySegment:
    def __init__(self, parent: "BodySegment" = None, color: tuple = (255, 255, 255)):
        self.parent = parent
        self.pos = pg.Vector2()
        self.space = 14
        self.color = color

    def update(self) -> None:
        if self.pos.distance_to(self.parent.pos) < self.space:
            return

        direction = self.pos - self.parent.pos
        direction.scale_to_length(self.space)
        self.pos = self.parent.pos + direction

