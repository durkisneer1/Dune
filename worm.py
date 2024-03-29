import pygame as pg


class Worm:
    def __init__(self):
        self.positions = []

    def update(self, dt: float, pos: pg.Vector2):
        pass


class BodySegment:
    def __init__(self):
        self.pos = pg.Vector2()
