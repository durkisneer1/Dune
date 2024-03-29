from typing import TYPE_CHECKING

import pygame as pg

if TYPE_CHECKING:
    from main import Game


class Tile:
    def __init__(self, game: "Game", pos: pg.Vector2, image: pg.Surface, name: str):
        self.game = game

        self.name = name
        self.image = image
        self.rect = self.image.get_frect(topleft=pos)

    def draw(self):
        self.game.screen.blit(self.image, self.rect.move(-self.game.camera))
