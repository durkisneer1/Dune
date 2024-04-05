from math import ceil
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import Game


class TimeLeft:
    def __init__(self, game: "Game"):
        self.game = game
        self.time_left = 90  # In seconds
        self.over = False

    def update(self):
        self.time_left -= self.game.dt
        if self.time_left <= 0:
            self.over = True
            return

    def draw(self):
        timer_surface = self.game.upheaval_font.render(
            f"Time: {ceil(self.time_left)}", True, (243, 246, 245)
        )

        shadow = self.game.upheaval_font.render(
            f"Time: {ceil(self.time_left)}", True, (48, 44, 46)
        )

        self.game.screen.blit(shadow, (11, 11))
        self.game.screen.blit(timer_surface, (10, 10))
