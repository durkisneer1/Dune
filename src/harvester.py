import pygame as pg
from typing import TYPE_CHECKING
from src.core.settings import *
from random import choice

if TYPE_CHECKING:
    from main import Game


class Harvester:
    def __init__(
        self,
        game: "Game",
        anim: list[pg.Surface],
        pos: pg.Vector2,
        direction: pg.Vector2,
    ):
        self.game = game
        self.anim = anim
        self.pos = pos
        self.direction = direction

        self.current_frame = 0
        self.frame = self.anim[self.current_frame]
        self.rect = self.frame.get_rect()
        self.speed = 25
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

        self.anim_speed = 5
        self.anim_length = len(self.anim)

        self.chased = False

    def animate(self):
        self.current_frame += self.anim_speed * self.game.dt
        self.current_frame %= self.anim_length
        self.frame = self.anim[int(self.current_frame)]

    def move(self, worm_head_pos: pg.Vector2):
        self.animate()

        self.pos += self.direction * self.speed * self.game.dt
        self.rect.center = self.pos

        if worm_head_pos.distance_to(self.pos) < 80:
            self.direction = (self.pos - worm_head_pos).normalize()

        grid_x, grid_y = self.pos.elementwise() // TILE_SIZE
        for dx, dy in self.directions:
            if (t := (grid_x + dx, grid_y + dy)) in self.game.collider_dict:
                if not self.game.collider_dict[t].rect.colliderect(self.rect):
                    continue

                empty_tiles = []
                for ddx, ddy in self.directions:
                    if (
                        t := (grid_x + ddx, grid_y + ddy)
                    ) not in self.game.collider_dict:
                        empty_tiles.append(t)
                random_tile = choice(empty_tiles)

                self.pos -= self.direction * self.speed * self.game.dt

                self.direction = pg.Vector2(random_tile) - pg.Vector2(grid_x, grid_y)
                if self.direction:
                    self.direction.normalize_ip()

                break

    def draw(self):
        image = pg.transform.rotozoom(
            self.frame, self.direction.angle_to(pg.Vector2(1, 0)) + 90, 1
        )
        self.rect = image.get_rect(center=self.pos)
        self.game.screen.blit(image, self.rect.move(-self.game.camera))
