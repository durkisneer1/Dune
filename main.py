import pygame as pg
from pytmx.util_pygame import load_pygame

from src.core.settings import *
from src.core.surfaces import load_tmx_layers
from src.enums import GameStates
from src.levels.arrow_level import ArrowLevel
from src.levels.lobby import LobbyLevel
from src.levels.ride_level import RideLevel
from src.levels.menu import Menu


class Game:
    def __init__(self):
        pg.init()

        self.screen = pg.display.set_mode((WIN_WIDTH, WIN_HEIGHT), pg.SCALED)
        self.clock = pg.Clock()
        self.camera = pg.Vector2()
        self.keys = ()
        self.dt = 0
        self.running = True

        self.ubuntu_font = pg.font.SysFont("Ubuntu", 16, True)
        self.ariel_font = pg.font.SysFont("Arial", 12)
        self.upheaval_font = pg.font.Font("assets/upheaval.ttf", 20)

        pg.display.set_caption("Dune")

        tile_set = load_pygame("assets/terrain.tmx")
        self.collision_tiles = []
        self.all_tiles = []
        self.sorted_tiles = []
        self.spawn_tiles = []
        load_tmx_layers(self, tile_set, "Harvester", self.spawn_tiles)
        load_tmx_layers(self, tile_set, "Sand", self.all_tiles)
        load_tmx_layers(self, tile_set, "Wall", (self.collision_tiles, self.all_tiles))
        load_tmx_layers(self, tile_set, "Tree", self.sorted_tiles)

        self.collider_dict = {}
        for tile in self.collision_tiles:
            self.collider_dict[
                (tile.rect.x // TILE_WIDTH, tile.rect.y // TILE_HEIGHT)
            ] = tile

        self.level_dict = {
            GameStates.MENU: Menu(self),
            GameStates.RIDE: RideLevel(self),
            GameStates.LOBBY: LobbyLevel(self),
            GameStates.ARROW: ArrowLevel(self),
        }
        self.current_level = GameStates.MENU

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
            level = self.level_dict[self.current_level]

            for event in pg.event.get():
                self.close(event)
                if self.current_level == GameStates.MENU:
                    level.handle_events(event)

            level.update()
            if level.next_state is not None:
                self.current_level = level.next_state
                self.level_dict[self.current_level].fade_transition.fade_in = True

            pg.display.flip()


if __name__ == "__main__":
    game = Game()
    game.run()
