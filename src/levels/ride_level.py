from typing import TYPE_CHECKING

from src.worm import Worm

if TYPE_CHECKING:
    from main import Game


class RideLevel:
    def __init__(self, game: "Game"):
        self.game = game

        self.worm = Worm(game)

    def update(self):
        self.game.screen.fill((30, 30, 30))
        self.worm.update()
        self.worm.draw()
