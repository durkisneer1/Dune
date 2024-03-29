import pygame
import time
import random
from src.core.animation import LoopType, Motion
from src.core.curves import *
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


class AccuracyStatus:
    def __init__(self) -> None:
        self.font = pygame.font.SysFont("Ubuntu", 16, True)
        self.zoom = Motion()
        self.zoom.add_frame(0.5, 1.0, 150, easing_type=ease_in_out_back)
        self.zoom.add_frame(1.0, 1.2, 150, easing_type=ease_in_back)
        self.zoom.add_frame(1.2, 1.0, 150, easing_type=ease_in_back)
        self.zoom.add_frame(1.0, 0.0, 150, easing_type=ease_in_out_expo)

        self.acurracy = ["Very Silly", "Kinda Silly", "Silly", "Not Silly", "Miss"]
        self.texts = [
            self.font.render(acurracy, True, "white") for acurracy in self.acurracy
        ]
        self.current_status = None
        self.acc_surface = None

        self.rect = None

    def update(self):
        self.zoom.update()
        if self.current_status != None:
            self.acc_surface = self.texts[self.current_status]
            self.rect = self.acc_surface.get_rect()
            self.rect.center = [50, 50]
        if self.zoom.is_playing():
            self.acc_surface = pygame.transform.smoothscale_by(
                self.texts[self.current_status], self.zoom.get_value()
            )
            self.rect = self.acc_surface.get_rect()
            self.rect.center = [50, 50]

    def fire_anim(self):
        self.zoom.play(1, LoopType.ONEWAY)

    def render(self, surface: pygame.Surface):
        if self.acc_surface:
            if self.zoom.is_playing():
                surface.blit(self.acc_surface, self.rect)


def is_between(value, _min, _max):
    return value < _max and value >= _min


class ArrowHUD:
    def __init__(self) -> None:
        self.acc_status = AccuracyStatus()

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

        self.bpm = 120
        self.offset = 2000
        self.begin = time.time()
        self.current_time = 0
        self.lanes = [
            [i * 250 * 2 for i in range(1, 120)],
            [i * 150 * 2 for i in range(1, 120)],
            [150 + i * 150 * 2 for i in range(1, 120)],
            [150 + i * 350 * 2 for i in range(1, 120)],
        ]
        self.fall_speed = 0.3

        self.keymaps = [pygame.K_x, pygame.K_c, pygame.K_COMMA, pygame.K_PERIOD]

        self.arrowtimestamp: list[Arrow] = []

    def update(self):
        just_pressed = pygame.key.get_just_pressed()
        self.current_time = (time.time() - self.begin) * 1000

        for idx, keymap in enumerate(self.keymaps):
            if not self.lanes[idx]:
                break
            if just_pressed[keymap]:
                nonabsdiff = self.current_time - self.lanes[idx][0] - self.offset
                diff = abs(nonabsdiff)

                if is_between(diff, 80, 100):
                    self.acc_status.current_status = 3
                    self.acc_status.fire_anim()
                    self.lanes[idx].pop(0)

                if is_between(diff, 50, 80):
                    self.acc_status.current_status = 2
                    self.acc_status.fire_anim()

                    self.lanes[idx].pop(0)

                if is_between(diff, 30, 50):
                    self.acc_status.current_status = 1
                    self.acc_status.fire_anim()

                    self.lanes[idx].pop(0)

                if is_between(diff, 0, 30):
                    self.acc_status.current_status = 0
                    self.acc_status.fire_anim()

                    self.lanes[idx].pop(0)
                print(self.acc_status.current_status, diff)
        self.acc_status.update()

    def render(self, surface: pygame.Surface):
        for idx, arrow in enumerate(self.arrows):
            surface.blit(arrow, [10 + idx * 20, 10])

        for lane_idx, lane in enumerate(self.lanes):
            for ts_idx, timestamp in enumerate(lane):
                timestamp = timestamp + self.offset
                if timestamp > self.current_time + 1000:
                    break
                if (timestamp - self.current_time) * self.fall_speed > 2000:
                    continue
                ypos = 10 + (timestamp - self.current_time) * self.fall_speed
                if ypos < -20:
                    # self.acc_status.current_status = 4
                    self.lanes[lane_idx].pop(ts_idx)
                else:
                    surface.blit(
                        self.arrows_tinted[lane_idx],
                        [
                            10 + lane_idx * 20,
                            ypos,
                        ],
                    )
        self.acc_status.render(surface)
