from typing import TYPE_CHECKING

import pygame as pg

if TYPE_CHECKING:
    from main import Game


class Worm:
    def __init__(self, game: "Game"):
        self.game = game

        self.head = BodySegment()
        self.segments = []
        for i in range(10):
            segment = BodySegment(
                self.head if i == 0 else self.segments[i - 1],
                (255 - i * 20, 255 - i * 20, 255 - i * 20)
            )
            self.segments.append(segment)
        self.segments.reverse()

    def update(self):
        self.head.pos.xy = pg.mouse.get_pos()
        for segment in self.segments:
            segment.update(self.game.dt)

    def draw(self):
        for segment in self.segments:
            pg.draw.circle(self.game.screen, segment.color, segment.pos, 8)


class BodySegment:
    def __init__(self, parent: "BodySegment" = None, color: tuple = (255, 255, 255)):
        self.parent = parent
        self.pos = pg.Vector2()
        self.space = 14
        self.color = color

    def update(self, dt: float) -> None:
        if self.pos.distance_to(self.parent.pos) < self.space:
            return

        direction = self.pos - self.parent.pos
        direction.scale_to_length(self.space)
        self.pos = self.parent.pos + direction

