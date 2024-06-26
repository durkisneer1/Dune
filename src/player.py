from typing import TYPE_CHECKING

import pygame as pg

from src.core.settings import *
from src.core.surfaces import import_image

if TYPE_CHECKING:
    from main import Game


class Player:
    def __init__(self, game: "Game"):
        self.game = game
        self.colliders = [tile.rect for tile in game.collision_tiles]

        self.image = import_image("assets/paul/right/idle/0.png")
        self.flipped = import_image("assets/paul/left/idle/0.png")

        self.pos = pg.Vector2(WORLD_WIDTH / 2, WORLD_HEIGHT / 2)
        self.rect = self.image.get_frect(center=self.pos)
        self.direction = pg.Vector2()
        self.speed = 100
        self.right = False

        self.directions = (
            (1, 0),
            (0, 1),
            (-1, 0),
            (0, -1),
            (1, 1),
            (-1, 1),
            (1, -1),
            (-1, -1),
        )

    def move(self):
        self.direction.xy = 0, 0
        if self.game.keys[pg.K_a]:
            self.direction.x -= 1
            self.right = False
        if self.game.keys[pg.K_d]:
            self.direction.x += 1
            self.right = True
        if self.game.keys[pg.K_w]:
            self.direction.y -= 1
        if self.game.keys[pg.K_s]:
            self.direction.y += 1

        if self.direction.length():
            self.direction.normalize_ip()
        velocity = self.direction * self.speed * self.game.dt

        self.pos.x += velocity.x
        self.h_collide()
        self.pos.y += velocity.y
        self.v_collide()

        self.game.camera = self.game.camera.lerp(
            self.pos - pg.Vector2(WIN_WIDTH / 2, WIN_HEIGHT / 2), self.game.dt * 3
        )

    def h_collide(self):
        self.rect.centerx = self.pos.x
        grid_x, grid_y = self.pos.elementwise() // TILE_SIZE
        for dx, dy in self.directions:
            if (t := (grid_x + dx, grid_y + dy)) in self.game.collider_dict:
                if not self.game.collider_dict[t].rect.colliderect(self.rect):
                    continue

                if self.direction.x > 0:
                    self.rect.right = self.game.collider_dict[t].rect.left
                elif self.direction.x < 0:
                    self.rect.left = self.game.collider_dict[t].rect.right
                self.pos.x = self.rect.centerx
                break

    def v_collide(self):
        self.rect.centery = self.pos.y
        grid_x, grid_y = self.pos.elementwise() // TILE_SIZE
        for dx, dy in self.directions:
            if (t := (grid_x + dx, grid_y + dy)) in self.game.collider_dict:
                if not self.game.collider_dict[t].rect.colliderect(self.rect):
                    continue

                if self.direction.y > 0:
                    self.rect.bottom = self.game.collider_dict[t].rect.top
                elif self.direction.y < 0:
                    self.rect.top = self.game.collider_dict[t].rect.bottom
                self.pos.y = self.rect.centery
                break

    def draw(self):
        img = self.image if self.right else self.flipped
        self.game.screen.blit(img, self.rect.move(-self.game.camera))
