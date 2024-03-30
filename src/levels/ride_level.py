from typing import TYPE_CHECKING

from src.worm import Worm
from src.core.particles import Particle

if TYPE_CHECKING:
    from main import Game


class RideLevel:
    def __init__(self, game: "Game"):
        self.game = game

        self.worm = Worm(game)

    def update(self):
        self.game.screen.fill((213, 242, 238))
        for tile in self.game.all_tiles:
            tile.draw()
        self.worm.update()
        self.worm.draw()

        for particle in Particle.particles:
            particle.update(self.game.dt)
            particle.draw(self.game.screen)
