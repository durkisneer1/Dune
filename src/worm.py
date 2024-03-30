from random import randint
from typing import TYPE_CHECKING

import pygame as pg

from src.core.particles import Particle
from src.core.settings import *
from src.core.surfaces import import_image

if TYPE_CHECKING:
    from main import Game


class Worm:
    def __init__(self, game: "Game"):
        self.game = game
        self.colliders = [tile.rect for tile in game.collision_tiles]

        self.head = BodySegment(image=import_image("assets/worm_head.png"))
        self.head_image = self.head.image
        self.head.pos.xy = WORLD_WIDTH / 2, WORLD_HEIGHT / 2
        self.head_rect = pg.Rect(self.head.pos, (10, 10))

        body_image = import_image("assets/worm_body.png")
        self.segments = []
        for i in range(9):
            segment = BodySegment(
                self.head if i == 0 else self.segments[i - 1], body_image
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
            segment.update(self.game.camera, self.game.dt)
        self.head_image = pg.transform.rotate(
            self.head.src_image, self.direction.angle_to(pg.Vector2(0, -1))
        )

        self.game.camera = self.game.camera.lerp(
            self.head.pos - pg.Vector2(WIN_WIDTH / 2, WIN_HEIGHT / 2), self.game.dt * 10
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
            rect = segment.image.get_rect(center=segment.pos - self.game.camera)
            self.game.screen.blit(segment.image, rect)

        rect = self.head_image.get_rect(center=self.head.pos - self.game.camera)
        self.game.screen.blit(self.head_image, rect)


class BodySegment:
    def __init__(self, parent: "BodySegment" = None, image: pg.Surface = None):
        self.parent = parent

        temp_surf = pg.Surface(image.get_rect().inflate(12, 12).size, pg.SRCALPHA)
        image_copy = image.copy()
        image_copy.set_alpha(200)
        temp_surf.blit(image_copy, (6, 6))
        temp_surf = pg.transform.gaussian_blur(temp_surf, 3, False)
        temp_surf.blit(image, (6, 6))
        self.src_image = temp_surf

        self.pos = pg.Vector2()
        self.space = 14
        self.image = self.src_image
        self.tick = 0

    def update(self, camera, dt) -> None:
        if self.pos.distance_to(self.parent.pos) < self.space:
            return

        direction = self.pos - self.parent.pos
        direction.scale_to_length(self.space)
        self.image = pg.transform.rotate(
            self.src_image, direction.angle_to(pg.Vector2(0, 1))
        )

        self.pos = self.parent.pos + direction

        self.tick += dt
        if self.tick > 0.2:
            self.tick = 0
            angle_offset = randint(-20, 20)
            direction.rotate_ip(angle_offset)
            Particle(
                self.pos - camera,
                direction * 10,
                (191, 121, 88),
                randint(1, 3) / 2,
                randint(1, 3),
            )
