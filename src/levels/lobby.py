from typing import TYPE_CHECKING

from src.player import Player
from src.core.settings import *

if TYPE_CHECKING:
    from main import Game


class LobbyLevel:
    def __init__(self, game: "Game"):
        self.game = game

        self.player = Player(game)
        self.game.camera = self.player.pos - (WIN_WIDTH / 2, WIN_HEIGHT / 2)

    def update(self):
        self.player.move()

        self.game.screen.fill((213, 242, 238))
        for tile in self.game.all_tiles:
            tile.draw()
        self.player.draw()
