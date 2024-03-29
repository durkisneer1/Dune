import pygame
import time
import random
from src.core.utils import *


class Arrow:
    def __init__(self, lane) -> None:
        self.lane = lane
        self.surface = pygame.Surface([20, 20], pygame.SRCALPHA)
        pygame.draw.circle(
            self.surface,
            "lightgreen",
            self.surface.get_rect().center,
            self.surface.get_rect().width // 2,
            0,
        )
        pygame.draw.circle(
            self.surface,
            "black",
            self.surface.get_rect().center,
            self.surface.get_rect().width // 2,
            1,
        )

    def render(self, surface: pygame.Surface):
        surface.blit(self.surface, [10, 10 + 30 * self.lane])


class ArrowHUD:
    def __init__(self) -> None:
        self.arrow_sheet = new_image_load("assets/arrows.png").convert_alpha()
        self.arrow_image = self.arrow_sheet.subsurface([0, 0, 20, 20])
        self.arrow_tinted = self.arrow_sheet.subsurface([20, 0, 20, 20])

        self.arrows = [
            pygame.transform.rotate(self.arrow_image, -90),
            self.arrow_image,
            pygame.transform.rotate(self.arrow_image, -180),
            pygame.transform.rotate(self.arrow_image, 90),
        ]
        self.arrows_tinted = [
            pygame.transform.rotate(self.arrow_tinted, -90),
            self.arrow_tinted,
            pygame.transform.rotate(self.arrow_tinted, -180),
            pygame.transform.rotate(self.arrow_tinted, 90),
        ]

        self.begin = time.time()
        self.current_time = 0
        self.lanes = [
            [i * 150 * 2 for i in range(1, 1250000)],
            [i * 150 * 2 for i in range(1, 1250000)],
            [150 + i * 150 * 2 for i in range(1, 1250000)],
            [150 + i * 150 * 2 for i in range(1, 1250000)],
        ]
        self.fall_speed = 0.1

        self.keymaps = [pygame.K_x, pygame.K_c, pygame.K_COMMA, pygame.K_PERIOD]

        self.arrowtimestamp: list[Arrow] = []

    def update(self):
        just_pressed = pygame.key.get_just_pressed()
        self.current_time = (time.time() - self.begin) * 1000
        for idx, keymap in enumerate(self.keymaps):
            if just_pressed[keymap]:
                diff = abs(self.current_time - self.lanes[idx][0])
                print(diff)
                if diff < 100:
                    self.lanes[idx].pop(0)
                    print("hit")

    def render(self, surface: pygame.Surface):
        for idx, arrow in enumerate(self.arrows):
            surface.blit(arrow, [10 + idx * 20, 10])
        for lane_idx, lane in enumerate(self.lanes):
            for ts_idx, timestamp in enumerate(lane):
                if timestamp > self.current_time + 1000:
                    break
                if (timestamp - self.current_time) * self.fall_speed > 2000:
                    continue
                ypos = 10 + (timestamp - self.current_time) * self.fall_speed
                if ypos < -20:
                    self.lanes[lane_idx].pop(ts_idx)
                else:
                    surface.blit(
                        self.arrows_tinted[lane_idx],
                        [
                            10 + lane_idx * 20,
                            ypos,
                        ],
                    )
