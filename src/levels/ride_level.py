from typing import TYPE_CHECKING
from random import choice

from src.core.particles import Particle
from src.worm import Worm
from src.harvester import Harvester
from src.explosion import Explosion
from src.levels.time_left import TimeLeft

if TYPE_CHECKING:
    from main import Game

import pygame

from src.core.fade import FadeTransition
from src.core.settings import *
from src.enums import GameStates
from src.core.surfaces import import_folder, import_anim


class RideLevel:
    def __init__(self, game: "Game"):
        self.game = game

        self.time_left = TimeLeft(game)
        self.worm = Worm(game)
        self.explosion_anim = import_anim("assets/explosion.png", 32, 32)

        harvester_anim = import_folder("assets/harvester")
        self.harvester_list = [
            Harvester(
                game,
                harvester_anim,
                choice(self.game.spawn_tiles).rect.center,
                pygame.Vector2(1, 0).rotate(choice(range(360))),
            )
            for _ in range(15)
        ]

        self.harvester_count = game.upheaval_font.render(
            f"Harvesters: {len(self.harvester_list)}", True, (243, 246, 245)
        )
        self.harvester_count_shadow = game.upheaval_font.render(
            f"Harvesters: {len(self.harvester_list)}", True, (48, 44, 46)
        )

        self.explosion_list = []

        self.next_state = None
        self.fade_transition = FadeTransition(True, TRANSITION_SPEED, WIN_SIZE)

    def reset(self):
        self.time_left = TimeLeft(self.game)
        self.worm = Worm(self.game)
        self.explosion_list = []
        self.harvester_list = [
            Harvester(
                self.game,
                import_folder("assets/harvester"),
                choice(self.game.spawn_tiles).rect.center,
                pygame.Vector2(1, 0).rotate(choice(range(360))),
            )
            for _ in range(15)
        ]

    def update(self):
        self.game.screen.fill((213, 242, 238))
        for tile in self.game.all_tiles:
            tile.draw()

        for particle in Particle.particles:
            particle.update(self.game.dt)
            particle.draw(self.game.screen)

        for harvester in self.harvester_list.copy():
            harvester.move(self.worm.head.pos)
            harvester.draw()
            if harvester.rect.collidepoint(self.worm.head.pos):
                Explosion(
                    self.game,
                    self.worm.head.pos,
                    self.explosion_anim,
                    self.explosion_list,
                )
                self.harvester_list.remove(harvester)
                self.harvester_count = self.game.upheaval_font.render(
                    f"Harvesters: {len(self.harvester_list)}", True, (243, 246, 245)
                )
                self.harvester_count_shadow = self.game.upheaval_font.render(
                    f"Harvesters: {len(self.harvester_list)}", True, (48, 44, 46)
                )

        self.worm.update()
        self.worm.draw()

        for explosion in self.explosion_list:
            explosion.animate()
            explosion.draw()

        self.time_left.update()
        self.time_left.draw()

        self.game.screen.blit(
            self.harvester_count_shadow,
            (WIN_WIDTH - self.harvester_count_shadow.get_width() - 9, 11),
        )
        self.game.screen.blit(
            self.harvester_count,
            (WIN_WIDTH - self.harvester_count.get_width() - 10, 10),
        )

        self.fade_transition.update(self.game.dt)
        self.fade_transition.draw(self.game.screen)

        self.next_state = None
        if self.time_left.over and self.fade_transition.fade_in:
            self.fade_transition.fade_in = False
            self.reset()
        if self.fade_transition.event:
            # level to switch to (arrow as a placeholder)
            self.next_state = GameStates.LOBBY
