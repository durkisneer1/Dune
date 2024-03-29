from pytmx.util_pygame import load_pygame

from src.player import Player
from src.core.utils import *

if TYPE_CHECKING:
    from main import Game


class LobbyLevel:
    def __init__(self, game: "Game"):
        self.game = game

        tile_set = load_pygame("assets/terrain.tmx")
        self.collision_tiles = []
        self.all_tiles = []
        load_tmx_layers(game, tile_set, "Sand", self.all_tiles)
        load_tmx_layers(game, tile_set, "Wall", (self.collision_tiles, self.all_tiles))
        load_tmx_layers(game, tile_set, "Tree", self.all_tiles)

        self.player = Player(game, [tile.rect for tile in self.collision_tiles])

    def update(self):
        self.player.move()

        self.game.screen.fill("white")
        for tile in self.all_tiles:
            tile.draw()
        self.player.draw()
