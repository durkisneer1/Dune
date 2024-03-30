import pygame as pg


class Particle:
    particles = []

    def __init__(
        self, pos: pg.Vector2, vel: pg.Vector2, color: tuple | str, lifetime: float, size: int
    ):
        self.pos = pg.Vector2(pos)
        self.vel = pg.Vector2(vel)
        self.color = color
        self.lifetime = lifetime
        self.size = size
        Particle.particles.append(self)

    def update(self, dt):
        self.pos += self.vel * dt
        self.lifetime -= dt
        if self.lifetime <= 0:
            Particle.particles.remove(self)

    def draw(self, screen):
        pg.draw.circle(screen, self.color, self.pos, self.size)
