import pygame as pg
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import Game


class Explosion:
    def __init__(
        self,
        game: "Game",
        pos: pg.Vector2,
        anim: list[pg.Surface],
        group: list["Explosion"],
    ):
        self.game = game
        self.anim = anim
        self.group = group
        group.append(self)

        self.current_frame = 0
        self.frame = self.anim[self.current_frame]
        self.rect = self.frame.get_frect(center=pos)

        self.anim_speed = 10
        self.anim_length = len(self.anim)

    def animate(self):
        self.current_frame += self.anim_speed * self.game.dt
        if self.current_frame > self.anim_length:
            self.group.remove(self)
            return
        self.frame = self.anim[int(self.current_frame)]

    def draw(self):
        self.game.screen.blit(self.frame, self.rect.move(-self.game.camera))
