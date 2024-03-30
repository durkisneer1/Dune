from typing import TYPE_CHECKING

from src.vsrg.hud import ArrowHUD

if TYPE_CHECKING:
    from main import Game

import pygame

from src.core.fade import FadeTransition
from src.core.settings import TRANSITION_SPEED, WIN_SIZE
from src.enums import GameStates


class ArrowLevel:
    def __init__(self, game: "Game"):
        self.game = game
        self.hud = ArrowHUD(game)

        self.next_state = None
        self.fade_transition = FadeTransition(True, TRANSITION_SPEED, WIN_SIZE)

    def update(self):
        self.game.screen.fill((213, 242, 238))
        for tile in self.game.all_tiles:
            tile.draw()
        self.hud.update()
        self.hud.draw()

        self.fade_transition.update(self.game.dt)
        self.fade_transition.draw(self.game.screen)

        just_pressed = pygame.key.get_just_pressed()
        self.next_state = None
        if just_pressed[pygame.K_SPACE]:
            self.fade_transition.fade_in = False
        if self.fade_transition.event:
            # level to switch to (lobby as a placeholder)
            self.next_state = GameStates.LOBBY
