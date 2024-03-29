from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import Game
from src.vsrg.hud import ArrowHUD


class ArrowLevel:
    def __init__(self, game: "Game") -> None:
        self.game = game
        self.hud = ArrowHUD()

    def update(self):
        self.hud.update()
        self.game.screen.fill("white")
        for tile in self.game.all_tiles:
            tile.draw()
        self.hud.render(self.game.screen)
