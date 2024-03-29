from typing import TYPE_CHECKING

from src.worm import Worm

if TYPE_CHECKING:
    from main import Game


class RideLevel:
    def __init__(self, game: "Game"):
        self.game = game

        self.worm = Worm(game)

    def update(self):
        self.game.screen.fill("white")
        for tile in self.game.all_tiles:
            tile.draw()
        self.worm.update()
        self.worm.draw()
