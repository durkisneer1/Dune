import pygame as pg


class Tile:
    def __init__(self, pos: pg.Vector2, image: pg.Surface, name: str):
        self.name = name
        self.image = image
        self.rect = self.image.get_rect(topleft=pos)
        self.hovered = False

    def draw(self, screen: pg.Surface, offset: pg.Vector2):
        screen.blit(self.image, self.rect.move(-offset))
