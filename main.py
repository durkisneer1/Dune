from pytmx.util_pygame import load_pygame

from utils import *
from player import Player

from vsrg.hud import ArrowHUD


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

        self.arrowhud = ArrowHUD()

    def close(self, event: pg.Event):
        if event.type == pg.QUIT:
            self.running = False
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                self.running = False

    def update(self):
        # pg.display.set_caption(f"{self.clock.get_fps():.1f} fps")
        self.keys = pg.key.get_pressed()
        self.player.move()
        self.arrowhud.update()

    def render(self):
        self.screen.fill((30, 30, 30))
        for tile in self.all_tiles:
            tile.draw()
        self.player.draw()

        self.arrowhud.render(self.screen)

        pg.display.flip()

    def run(self):
        while self.running:
            self.dt = self.clock.tick(60) / 1000
            for event in pg.event.get():
                self.close(event)
            self.update()
            self.render()


if __name__ == "__main__":
    game = Game()
    game.run()
