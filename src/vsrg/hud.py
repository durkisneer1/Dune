import time
from bisect import bisect_right
from typing import TYPE_CHECKING

import pygame as pg
from src.core.settings import *
from src.core.curves import *
from src.core.animation import LoopType, Motion
from src.core.surfaces import import_image

if TYPE_CHECKING:
    from main import Game


class AccuracyStatus:
    def __init__(self, game: "Game"):
        self.game = game

        self.font = pg.font.SysFont("Ubuntu", 16, True)
        self.zoom = Motion()
        self.zoom.add_frame(0.9, 1.3, 50, easing_type=ease_in_back)
        self.zoom.add_frame(1.3, 1.0, 250, easing_type=ease_out_back)

        self.accuracy = ["PERFECT", "GREAT", "GOOD", "BAD", "MISS"]
        self.texts = [
            self.make_text_surface(accuracy, color)
            for accuracy, color in zip(
                self.accuracy, ["green", "lightblue", "yellow", "gray", "red"]
            )
        ]
        self.current_status = None
        self.acc_surface = None

        self.rect = None

    def make_text_surface(self, text, color):
        original = self.font.render(text, False, "white")
        colored = self.font.render(text, False, color)

        surf = pg.Surface(
            [original.get_width(), original.get_height() + 2], pg.SRCALPHA
        )
        surf.blit(colored, [0, 1])
        surf.blit(original, [0, 0])
        return surf

    def make_surface_rect(self):
        self.rect = self.acc_surface.get_rect()
        self.rect.center = [50, 50]

    def update(self):
        self.zoom.update()
        if self.current_status is not None:
            self.acc_surface = self.texts[self.current_status]
            self.make_surface_rect()
        if self.zoom.is_playing():
            self.acc_surface = pg.transform.scale_by(
                self.texts[self.current_status], self.zoom.get_value()
            )
            self.make_surface_rect()

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

        self.static_arrows = [
            pg.transform.rotate(self.arrow_image, -90),
            self.arrow_image,
            pg.transform.rotate(self.arrow_image, -180),
            pg.transform.rotate(self.arrow_image, 90),
        ]
        self.falling_arrows = [
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
            [i * 2000 for i in range(1, 120)],
            [100 + i * 2300 for i in range(1, 120)],
            [200 + i * 2500 for i in range(1, 120)],
            [300 + i * 1200 for i in range(1, 120)],
        ]
        self.fall_speed = 0.1

        self.misses = 0

        self.keymaps = [pg.K_d, pg.K_f, pg.K_j, pg.K_k]

        self.bg_surface = pg.Surface([80, WIN_HEIGHT], flags=pg.SRCALPHA)
        self.bg_surface.fill("black")
        self.bg_surface.set_alpha(150)

        self.lane_press = pg.Surface([1, 5], flags=pg.SRCALPHA)
        self.lane_press.set_at([0, 0], "white")
        self.lane_press.set_at([0, 1], "white")
        self.lane_press = pg.transform.smoothscale(self.lane_press, [20, WIN_HEIGHT])

        self.lane_surfaces = [self.lane_press.copy() for i in range(4)]

        self.lane_fades: list[Motion] = []
        for i in range(4):
            press_alpha = Motion()
            press_alpha.add_frame(0, 60, 50, ease_in_sine)
            press_alpha.add_frame(60, 0, 250, ease_in_sine)
            self.lane_fades.append(press_alpha)

    def update(self):
        just_pressed = pg.key.get_just_pressed()
        self.current_time = (time.time() - self.begin) * 1000
        for lane, fade in zip(self.lane_surfaces, self.lane_fades):
            fade.update()
            lane.set_alpha(fade.get_value())

        for lane_idx, (keymap, lane) in enumerate(zip(self.keymaps, self.lanes)):
            if just_pressed[keymap] and lane:
                self.lane_fades[lane_idx].play(1, LoopType.ONEWAY)
                non_abs_diff = self.current_time - lane[0] - self.offset
                diff = abs(non_abs_diff)
                if 0 <= diff < 200:
                    self.acc_status.current_status = bisect_right([70, 120, 200], diff)
                    self.acc_status.fire_anim()
                    lane.pop(0)

        self.acc_status.update()

    def draw(self):
        self.bg_surface.fill("black")
        self.bg_surface.set_alpha(130)
        for idx, lane in enumerate(self.lane_surfaces):
            self.bg_surface.blit(lane, [idx * 20, 0])

        pg.draw.line(self.bg_surface, "white", [0, 0], [0, WIN_HEIGHT])
        pg.draw.line(self.bg_surface, "white", [79, 0], [79, WIN_HEIGHT])

        self.game.screen.blit(self.bg_surface, [10, 0])
        for idx, (arrow, arrow_tinted) in enumerate(
            zip(self.static_arrows, self.falling_arrows)

        ):
            self.game.screen.blit(arrow, [10 + idx * 20, 10])

        for lane_idx, lane in enumerate(self.lanes):
            for ts_idx, timestamp in enumerate(lane):
                timestamp = timestamp + self.offset
                if timestamp > self.current_time + 4000:
                    break
                fall_speed = (timestamp - self.current_time) * self.fall_speed
                if fall_speed > 2000:
                    continue
                y_pos = 10 + fall_speed
                if y_pos < -20:
                    self.acc_status.current_status = 4
                    self.acc_status.fire_anim()
                    self.misses += 1
                    self.lanes[lane_idx].pop(ts_idx)
                else:
                    self.game.screen.blit(

                        self.falling_arrows[lane_idx], [10 + lane_idx * 20, y_pos]

                    )
        self.acc_status.draw()
