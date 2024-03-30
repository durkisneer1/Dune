import pygame as pg
from pytmx.util_pygame import load_pygame

from src.core.settings import *
from src.core.surfaces import load_tmx_layers
from src.enums import GameStates
from src.levels.arrow_level import ArrowLevel
from src.levels.lobby import LobbyLevel
from src.levels.ride_level import RideLevel


class Game:
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode((WIN_WIDTH, WIN_HEIGHT), pg.SCALED)
        pg.display.set_caption("Dune")
        self.clock = pg.Clock()
        self.camera = pg.Vector2()
        self.keys = ()
        self.dt = 0
        self.running = True

        tile_set = load_pygame("assets/terrain.tmx")
        self.collision_tiles = []
        self.all_tiles = []
        load_tmx_layers(self, tile_set, "Sand", self.all_tiles)
        load_tmx_layers(self, tile_set, "Wall", (self.collision_tiles, self.all_tiles))
        load_tmx_layers(self, tile_set, "Tree", self.all_tiles)

        self.level_dict = {
            GameStates.RIDE: RideLevel(self),
            GameStates.LOBBY: LobbyLevel(self),
            GameStates.ARROW: ArrowLevel(self),
        }
        self.current_level = GameStates.LOBBY

    def close(self, event: pg.Event):
        if event.type == pg.QUIT:
            self.running = False
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                self.running = False

    def run(self):
        while self.running:
            self.dt = pg.math.clamp(self.clock.tick() / 1000, 0.001, 0.05)
            self.keys = pg.key.get_pressed()

            for event in pg.event.get():
                self.close(event)

            level = self.level_dict[self.current_level]
            level.update()
            if level.next_state is not None:
                self.current_level = level.next_state
                self.level_dict[self.current_level].fade_transition.fade_in = True

            pg.display.flip()


if __name__ == "__main__":
    game = Game()
    game.run()
