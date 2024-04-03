from __future__ import annotations

import time
from typing import TYPE_CHECKING

from src.core.settings import *
from src.player import Player

if TYPE_CHECKING:
    from main import Game

import pygame

from src.core.fade import FadeTransition
from src.core.settings import TRANSITION_SPEED, WIN_SIZE
from src.enums import GameStates


class DayNightCycle:
    def __init__(self, level: LobbyLevel) -> None:
        self.level = level
        self.opacity = 0
        self.surface = pygame.Surface(
            self.level.game.screen.get_size(), pygame.SRCALPHA
        )
        self.surface.fill([0, 0, 20])
        self.surface.set_alpha(self.opacity)

        self.begin = time.time()
        self.time = 0

        self.cycle_length = 120

        self.night_begin = 10
        self.night_transition_complete = 24

        self.day_begin = 80
        self.day_transition_complete = 90

        self.clock_sprite = self.make_clock()
        self.clockcopy = self.clock_sprite.copy()
        self.clock_rect = self.clock_sprite.get_rect(center=[20, 20])

    def make_clock(self):
        clocksize = [40, 40]
        surface = pygame.Surface(clocksize, pygame.SRCALPHA)

        day_begins_fade = 6.28 * self.night_begin / self.cycle_length

        night_start = (
            6.28
            * (self.night_transition_complete - self.night_begin)
            / self.cycle_length
            + day_begins_fade
        )

        night_begins_fade = (
            6.28 * (self.day_begin - self.night_transition_complete) / self.cycle_length
            + night_start
        )

        day_start = (
            6.28 * (self.day_transition_complete - self.day_begin) / self.cycle_length
            + night_begins_fade
        )

        pygame.draw.circle(
            surface,
            [30, 80, 230],
            pygame.Rect(0, 0, *clocksize).center,
            5 + clocksize[0] // 3,
        )
        pygame.draw.arc(
            surface,
            "yellow",
            [0, 0, *clocksize],
            0,
            day_begins_fade,
            5,
        )
        pygame.draw.arc(
            surface,
            "orange",
            [0, 0, *clocksize],
            day_begins_fade,
            night_start,
            5,
        )
        pygame.draw.arc(
            surface, "black", [0, 0, *clocksize], night_start, night_begins_fade, 5
        )
        pygame.draw.arc(
            surface, "orange", [0, 0, *clocksize], night_begins_fade, day_start, 5
        )
        pygame.draw.arc(surface, "yellow", [0, 0, *clocksize], day_start, 6.28, 5)
        surface = pygame.transform.rotate(surface, 90)
        surface = pygame.transform.flip(surface, True, False)

        return surface

    def update(self):
        self.time = 1000 * (time.time() - self.begin) % (self.cycle_length * 1000)
        self.clock_sprite = pygame.transform.rotate(
            self.clockcopy, 360 * self.time / (self.cycle_length * 1000)
        )
        self.clock_rect = self.clock_sprite.get_rect(center=[25, 25])
        if (
            self.time > self.night_begin * 1000
            and self.time < self.night_transition_complete * 1000
        ):
            self.opacity = 150 - 150 * (
                self.night_transition_complete * 1000 - self.time
            ) / ((self.night_transition_complete - self.night_begin) * 1000)
            self.surface.set_alpha(self.opacity)

        if (
            self.time > self.day_begin * 1000
            and self.time < self.day_transition_complete * 1000
        ):
            self.opacity = (
                150
                * (self.day_transition_complete * 1000 - self.time)
                / ((self.day_transition_complete - self.day_begin) * 1000)
            )
            self.surface.set_alpha(self.opacity)

    def draw(self):
        self.level.game.screen.blit(self.surface, [0, 0])
        self.level.game.screen.blit(self.clock_sprite, self.clock_rect)
        pygame.draw.line(
            self.level.game.screen,
            "white",
            self.clock_rect.center,
            [self.clock_rect.centerx, self.clock_rect.centery - 15],
        )


class LobbyLevel:
    def __init__(self, game: "Game"):
        self.game = game

        self.player = Player(game)
        self.game.sorted_tiles.append(self.player)
        self.game.camera = self.player.pos - (WIN_WIDTH / 2, WIN_HEIGHT / 2)

        self.cycle = DayNightCycle(self)

        self.next_state = None
        self.fade_transition = FadeTransition(True, TRANSITION_SPEED, WIN_SIZE)

    def update(self):
        self.cycle.update()
        self.player.move()

        self.game.screen.fill((213, 242, 238))
        self.game.sorted_tiles.sort(key=lambda t: t.rect.bottom)
        for tile in self.game.all_tiles + self.game.sorted_tiles:
            tile.draw()

        self.cycle.draw()

        self.fade_transition.update(self.game.dt)
        self.fade_transition.draw(self.game.screen)

        just_pressed = pygame.key.get_just_pressed()
        self.next_state = None
        if just_pressed[pygame.K_SPACE]:
            self.fade_transition.fade_in = False
        if self.fade_transition.event:
            # level to switch to (ride as a placeholder)
            self.next_state = GameStates.RIDE
