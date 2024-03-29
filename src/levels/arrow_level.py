from typing import TYPE_CHECKING

from src.vsrg.hud import ArrowHUD

if TYPE_CHECKING:
    from main import Game


class ArrowLevel:
    def __init__(self, game: "Game"):
        self.game = game
        self.hud = ArrowHUD(game)

    def update(self):
        self.game.screen.fill("white")
        for tile in self.game.all_tiles:
            tile.draw()
        self.hud.update()
        self.hud.draw()
