import time
from bisect import bisect_right
from typing import TYPE_CHECKING

import pygame as pg

from src.core.curves import *
from src.core.animation import LoopType, Motion
from src.core.surfaces import import_image

if TYPE_CHECKING:
    from main import Game


class Arrow:
    def __init__(self, lane, game: "Game"):
        self.game = game

        self.lane = lane
        self.surface = pg.Surface([20, 20], pg.SRCALPHA)
        pg.draw.circle(
            self.surface,
            "lightgreen",
            self.surface.get_rect().center,
            self.surface.get_rect().width // 2,
            0,
        )
        pg.draw.circle(
            self.surface,
            "black",
            self.surface.get_rect().center,
            self.surface.get_rect().width // 2,
            1,
        )

    def draw(self):
        self.game.screen.blit(self.surface, [10, 10 + 30 * self.lane])


class AccuracyStatus:
    def __init__(self, game: "Game"):
        self.game = game

        self.font = pg.font.SysFont("Ubuntu", 16, True)
        self.zoom = Motion()
        self.zoom.add_frame(0.5, 1.0, 150, easing_type=ease_in_out_back)
        self.zoom.add_frame(1.0, 1.2, 150, easing_type=ease_in_back)
        self.zoom.add_frame(1.2, 1.0, 150, easing_type=ease_in_back)
        self.zoom.add_frame(1.0, 0.0, 350, easing_type=ease_in_out_expo)

        self.accuracy = ["Very Silly", "Kinda Silly", "Silly", "Not Silly", "Miss"]
        self.texts = [
            (
                self.font.render(accuracy, True, "green")
                if accuracy != "Miss"
                else self.font.render(accuracy, True, "red")
            )
            for accuracy in self.accuracy
        ]
        self.current_status = None
        self.acc_surface = None

        self.rect = None

    def update(self):
        self.zoom.update()
        if self.current_status is not None:
            self.acc_surface = self.texts[self.current_status]
            self.rect = self.acc_surface.get_rect()
            self.rect.center = [50, 50]
        if self.zoom.is_playing():
            self.acc_surface = pg.transform.smoothscale_by(
                self.texts[self.current_status], self.zoom.get_value()
            )
            self.rect = self.acc_surface.get_rect()
            self.rect.center = [50, 50]

    def fire_anim(self):
        self.zoom.play(1, LoopType.ONEWAY)

    def draw(self):
        if self.acc_surface:
            if self.zoom.is_playing():
                self.game.screen.blit(self.acc_surface, self.rect)


class ArrowHUD:
    def __init__(self, game: "Game"):
        self.game = game

        self.acc_status = AccuracyStatus(game)

        self.arrow_sheet = import_image("assets/arrows.png")
        self.arrow_image = self.arrow_sheet.subsurface([0, 0, 20, 20])
        self.arrow_tinted = self.arrow_sheet.subsurface([20, 0, 20, 20])

        self.arrows = [
            pg.transform.rotate(self.arrow_image, -90),
            self.arrow_image,
            pg.transform.rotate(self.arrow_image, -180),
            pg.transform.rotate(self.arrow_image, 90),
        ]
        self.arrows_tinted = [
            pg.transform.rotate(self.arrow_tinted, -90),
            self.arrow_tinted,
            pg.transform.rotate(self.arrow_tinted, -180),
            pg.transform.rotate(self.arrow_tinted, 90),
        ]

        self.bpm = 120
        self.offset = 2000
        self.begin = time.time()
        self.current_time = 0
        self.lanes = [
            [i * 250 * 5 for i in range(1, 120)],
            [i * 150 * 5 for i in range(1, 120)],
            [150 + i * 150 * 5 for i in range(1, 120)],
            [150 + i * 350 * 5 for i in range(1, 120)],
        ]
        self.fall_speed = 0.3

        self.keymaps = [pg.K_x, pg.K_c, pg.K_COMMA, pg.K_PERIOD]

    def update(self):
        just_pressed = pg.key.get_just_pressed()
        self.current_time = (time.time() - self.begin) * 1000

        for keymap, lane in zip(self.keymaps, self.lanes):
            if just_pressed[keymap] and lane:
                non_abs_diff = self.current_time - lane[0] - self.offset
                diff = abs(non_abs_diff)
                if 0 <= diff < 100:
                    self.acc_status.current_status = bisect_right([30, 50, 80], diff)
                    self.acc_status.fire_anim()
                    lane.pop(0)

        self.acc_status.update()

    def draw(self):
        for idx, (arrow, arrow_tinted) in enumerate(
            zip(self.arrows, self.arrows_tinted)
        ):
            self.game.screen.blit(arrow, [10 + idx * 20, 10])

        for lane_idx, lane in enumerate(self.lanes):
            for ts_idx, timestamp in enumerate(lane):
                timestamp = timestamp + self.offset
                if timestamp > self.current_time + 1000:
                    break
                fall_speed = (timestamp - self.current_time) * self.fall_speed
                if fall_speed > 2000:
                    continue
                y_pos = 10 + fall_speed
                if y_pos < -20:
                    self.acc_status.current_status = 4
                    self.acc_status.fire_anim()
                    self.lanes[lane_idx].pop(ts_idx)
                else:
                    self.game.screen.blit(
                        self.arrows_tinted[lane_idx], [10 + lane_idx * 20, y_pos]
                    )
        self.acc_status.draw()
