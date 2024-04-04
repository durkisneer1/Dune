from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from main import Game

import pygame

from src.core.fade import FadeTransition
from src.core.settings import TRANSITION_SPEED, WIN_SIZE
from src.enums import GameStates


class Menu:
    def __init__(self, game: "Game"):
        self.game = game
        self.title = pygame.font.SysFont("Arial", 70)
        self.options_font = pygame.font.SysFont("Arial", 12)

        self.dune = self.title.render("Dune", False, "white")
        self.play = self.options_font.render("play", False, "white")
        self.options = self.options_font.render("options", False, "white")
        self.quit = self.options_font.render("quit", False, "white")

        self.next_state = None
        self.fade_transition = FadeTransition(True, TRANSITION_SPEED, WIN_SIZE)

    def handle_events(self, event):
        if event.type != pygame.MOUSEBUTTONDOWN:
            return

        if pygame.Rect([10, 120, *self.play.get_size()]).collidepoint(event.pos):
            self.fade_transition.fade_in = False
            if self.fade_transition.event:
                self.next_state = GameStates.LOBBY

        elif pygame.Rect([10, 145, *self.options.get_size()]).collidepoint(event.pos):
            print("'Options' screen not implemented yet")

        elif pygame.Rect([10, 170, *self.quit.get_size()]).collidepoint(event.pos):
            exit(0)

    def update(self):
        self.game.screen.fill("#ff7f27")
        pygame.draw.circle(self.game.screen, "#ffc90e", [-230, 80], 500)
        pygame.draw.circle(self.game.screen, "black", [-270, 80], 500)
        pygame.draw.polygon(
            self.game.screen, "#ffc90e", [[262, 163], [1316, 720], [244, 239]], 0
        )
        pygame.draw.circle(self.game.screen, "#ff7f27", [304 + 17, 162 + 19], 60)

        self.game.screen.blit(self.dune, [10, 10])
        self.game.screen.blit(self.play, [10, 120])
        self.game.screen.blit(self.options, [10, 145])
        self.game.screen.blit(self.quit, [10, 170])

        self.fade_transition.update(self.game.dt)
        self.fade_transition.draw(self.game.screen)

        just_pressed = pygame.key.get_just_pressed()
        self.next_state = None
        if just_pressed[pygame.K_SPACE]:
            self.fade_transition.fade_in = False
        if self.fade_transition.event:
            # level to switch to (arrow as a placeholder)
            self.next_state = GameStates.ARROW
