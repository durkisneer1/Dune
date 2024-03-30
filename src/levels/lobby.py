from typing import TYPE_CHECKING

from src.core.settings import *
from src.player import Player

if TYPE_CHECKING:
    from main import Game

import pygame

from src.core.fade import FadeTransition
from src.core.settings import TRANSITION_SPEED, WIN_SIZE
from src.enums import GameStates


class LobbyLevel:
    def __init__(self, game: "Game"):
        self.game = game

        self.player = Player(game)
        self.game.sorted_tiles.append(self.player)
        self.game.camera = self.player.pos - (WIN_WIDTH / 2, WIN_HEIGHT / 2)

        self.next_state = None
        self.fade_transition = FadeTransition(True, TRANSITION_SPEED, WIN_SIZE)

    def update(self):
        self.player.move()

        self.game.screen.fill((213, 242, 238))
        self.game.sorted_tiles.sort(key=lambda t: t.rect.bottom)
        for tile in self.game.all_tiles + self.game.sorted_tiles:
            tile.draw()

        self.fade_transition.update(self.game.dt)
        self.fade_transition.draw(self.game.screen)

        just_pressed = pygame.key.get_just_pressed()
        self.next_state = None
        if just_pressed[pygame.K_SPACE]:
            self.fade_transition.fade_in = False
        if self.fade_transition.event:
            # level to switch to (ride as a placeholder)
            self.next_state = GameStates.RIDE
