from typing import TYPE_CHECKING

from src.player import Player

if TYPE_CHECKING:
    from main import Game


class LobbyLevel:
    def __init__(self, game: "Game"):
        self.game = game

        self.player = Player(game, [tile.rect for tile in game.collision_tiles])

    def update(self):
        self.player.move()

        self.game.screen.fill("white")
        for tile in self.game.all_tiles:
            tile.draw()
        self.player.draw()
