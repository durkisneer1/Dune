from pytmx.util_pygame import load_pygame

from utils import *
from player import Player


class Game:
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode((WIN_WIDTH, WIN_HEIGHT), pg.SCALED)
        pg.display.set_caption("Dune")
        self.clock = pg.Clock()

        self.keys = ()
        self.dt = 0
        self.running = True
        self.fps_tracker = {}

        tile_set = load_pygame("assets/terrain.tmx")
        self.collision_tiles = []
        self.all_tiles = []
        load_tmx_layers(self, tile_set, "Sand", self.all_tiles)
        load_tmx_layers(self, tile_set, "Wall", (self.collision_tiles, self.all_tiles))
        load_tmx_layers(self, tile_set, "Tree", self.all_tiles)

        self.player = Player(self, [tile.rect for tile in self.collision_tiles])

        self.camera = pg.Vector2()

    def close(self, event: pg.Event):
        if event.type == pg.QUIT:
            self.running = False
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                self.running = False

    def run(self):
        while self.running:
            self.dt = self.clock.tick() / 1000
            self.keys = pg.key.get_pressed()

            for event in pg.event.get():
                self.close(event)

            self.player.move()

            self.screen.fill((30, 30, 30))
            for tile in self.all_tiles:
                tile.draw()
            self.player.draw()

            pg.display.flip()


if __name__ == "__main__":
    game = Game()
    game.run()
