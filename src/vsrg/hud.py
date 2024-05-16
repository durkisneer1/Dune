import os
from typing import TYPE_CHECKING

import time
import pickle

from copy import deepcopy

from bisect import bisect_right

import pygame as pg

from src.core.animation import LoopType, Motion
from src.core.curves import *
from src.core.settings import *
from src.core.surfaces import import_image

if TYPE_CHECKING:
    from main import Game

"""Delete this also when shipping because bloat"""


class Cache:
    def __init__(self) -> None:
        self.fft = None
        self.samples = None
        self.stft = None


class MusicAnalyzer:
    def __init__(self, path) -> None:
        self.music_length = pg.mixer.Sound(path).get_length()
        self.path = path
        self.cache = self.load_cache()

        self.stft = self.cache.stft
        self.frames_lapsed = 0
        self.samples = self.cache.samples
        self.sample_idx = 0
        self.hop = 1 / 1440
        self.indices = self.cache.fft

    @staticmethod
    def load_cache():
        with open("assets/fft.pkl", "rb") as file:
            return pickle.load(file)

    def cache_analysis(self):
        with open("assets/fft.pkl", "wb") as file:
            cache = Cache()
            cache.fft = self.indices
            cache.stft = self.stft
            cache.samples = self.samples
            pickle.dump(cache, file)

    def beat_idx(self, sample_idx):
        if sample_idx >= self.samples:
            return 0
        return sum(self.indices[:, sample_idx][::-1]) / len(
            self.indices[:, sample_idx][::-1]
        )

    def beat_idx_ms(self, ms):
        ratio = ms / (self.music_length * 1000)
        return self.beat_idx(int(ratio * self.samples))


class AccuracyStatus:
    def __init__(self, game: "Game"):
        self.game = game

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
        original = self.game.ubuntu_font.render(text, False, "white")
        colored = self.game.ubuntu_font.render(text, False, color)

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

        self.music_analyzer = MusicAnalyzer("assets/dune.ogg")

        self.music_length = self.music_analyzer.music_length

        self.editor_beat_data = []
        for i in range(
            0, self.music_analyzer.samples, self.music_analyzer.samples // WIN_HEIGHT
        ):
            self.editor_beat_data.append(self.music_analyzer.beat_idx(i))
        self.max_beat = max(self.editor_beat_data)
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

        self.bpm = 90
        self.offset = 2000
        self.begin = time.time()
        self.current_time = 0
        self.lanes = [
            [],
            [],
            [],
            [],
        ]
        if os.path.exists("assets/mapdata.pkl"):
            print("NOTE: Map data found")
            with open("assets/mapdata.pkl", "rb") as file:
                self.lanes = pickle.load(file)

        self.editor_lanes = deepcopy(self.lanes)

        self.fall_speed = 4

        self.misses = 0

        self.keymaps = [pg.K_d, pg.K_f, pg.K_j, pg.K_k]

        self.bg_surface = pg.Surface([80, WIN_HEIGHT], flags=pg.SRCALPHA)
        self.bg_surface.fill("black")
        self.bg_surface.set_alpha(150)

        self.lane_press = pg.Surface([1, 5], flags=pg.SRCALPHA)
        self.lane_press.set_at([0, 0], "white")
        self.lane_press.set_at([0, 1], "white")
        self.lane_press = pg.transform.smoothscale(self.lane_press, [20, WIN_HEIGHT])

        self.lane_surfaces = [self.lane_press.copy() for _ in range(4)]

        self.lane_fades: list[Motion] = []
        for i in range(4):
            press_alpha = Motion()
            press_alpha.add_frame(0, 60, 50, ease_in_sine)
            press_alpha.add_frame(60, 0, 250, ease_in_sine)
            self.lane_fades.append(press_alpha)

        self.editor = False

        self.pressed = False

        self.time_controls_rect = pg.Rect(0, 0, 0, 0)
        self.time_controls_rect.width = 50
        self.time_controls_rect.height = WIN_HEIGHT
        self.time_controls_rect.right = WIN_WIDTH

        self.wave_data_rect = pg.Rect(0, 0, 0, 0)
        self.wave_data_rect.width = 100
        self.wave_data_rect.height = WIN_HEIGHT
        self.wave_data_rect.right = WIN_WIDTH - 50

        self.begin_playing_ms = 0
        self.current_ms = 0
        self.play_ts = 0
        self.pause_music = False
        self.playing = False

        self.right_pressed = False
        self.hover_lane = 0
        self.hover_ts = 0

    def init_proc(self):
        ...

    def update_lane_alpha_values(self):
        for lane, fade in zip(self.lane_surfaces, self.lane_fades):
            fade.update()
            lane.set_alpha(fade.get_value())

    def update_curr_time(self):
        self.current_time = (time.time() - self.begin) * 1000

    def proc_key_presses(self, keys):
        for lane_idx, (keymap, lane) in enumerate(zip(self.keymaps, self.lanes)):
            if keys[keymap]:
                self.lane_fades[lane_idx].play(1, LoopType.ONEWAY)
                if lane:
                    non_abs_diff = self.current_ms - lane[0]
                    diff = abs(non_abs_diff)
                    if 0 <= diff < 200:
                        self.acc_status.current_status = bisect_right(
                            [70, 120, 200], diff
                        )
                        self.acc_status.fire_anim()
                        lane.pop(0)

    @staticmethod
    def unpause():
        """
        silly ahh mixer makes the song start all over again :anger:
        """
        pg.mixer.music.unpause()

    def play(self, s=0):
        pg.mixer.music.play(start=s)
        self.begin_playing_ms = s * 1000
        self.play_ts = time.time()
        self.playing = True

    def pause(self):
        pg.mixer.music.fadeout(400)
        self.playing = False

    def is_editor_accessed(self, keys):
        if keys[pg.K_F2]:
            self.editor = not self.editor
            if not self.editor:
                self.lanes = deepcopy(self.editor_lanes)
                with open("assets/mapdata.pkl", "wb") as file:
                    pickle.dump(self.lanes, file)

    def proc_song_pos(self):
        mouse_pos = pg.mouse.get_pos()

        if self.time_controls_rect.collidepoint(mouse_pos):
            ratio = mouse_pos[1] / self.time_controls_rect.height
            if self.playing:
                self.play(ratio * self.music_length)
            else:
                self.current_ms = ratio * self.music_length * 1000

    def add_note(self):
        mouse = pg.mouse.get_pos()
        y = mouse[1]
        hover_ts = self.current_ms + (y - 20) * self.fall_speed
        hover_lane = (mouse[0] - 10) // 20
        if hover_lane > 3 or hover_lane < 0:
            return
        self.editor_lanes[hover_lane].append(hover_ts)
        self.editor_lanes[hover_lane].sort()
        self.lanes = self.editor_lanes.copy()

    def delete_note(self):
        mouse = pg.mouse.get_pos()
        y = mouse[1]
        hover_ts = self.current_ms + (y - 20) * self.fall_speed
        hover_lane = (mouse[0] - 10) // 20
        if hover_lane > 3 or hover_lane < 0:
            return
        for ts in self.editor_lanes[hover_lane]:
            if abs(hover_ts - ts) < self.fall_speed * 10:
                self.editor_lanes[hover_lane].remove(ts)
                break
        self.editor_lanes[hover_lane].sort()
        self.lanes = self.editor_lanes.copy()

    def proc_left_click(self):
        """
        since there is no access to the event pipeline ill go with this silly solution
        """
        mouse = pg.mouse.get_pressed(3)

        if mouse[0] and not self.pressed:
            self.proc_song_pos()
            self.add_note()
            self.pressed = True
        if not mouse[0]:
            self.pressed = False

    def proc_right_click(self):
        mouse = pg.mouse.get_pressed(3)
        if mouse[2] and not self.right_pressed:
            self.delete_note()
            self.right_pressed = True

        if not mouse[2]:
            self.right_pressed = False

    def proc_editor_keys(self, keys):
        if keys[pg.K_p]:
            self.pause_music = not self.pause_music
            self.pause() if self.pause_music else self.play((self.current_ms / 1000))
        if keys[pg.K_F1]:
            with open("assets/mapdata.pkl", "wb") as file:
                pickle.dump(self.lanes, file)

    def update(self):
        rel = pg.mouse.get_rel()
        keys = pg.key.get_just_pressed()
        self.is_editor_accessed(keys)
        if self.editor:
            if self.playing:
                self.current_ms = (
                    time.time() - self.play_ts
                ) * 1000 + self.begin_playing_ms
            else:
                if pg.mouse.get_pressed(3)[1]:
                    self.current_ms -= rel[1] * 3
            self.proc_editor_keys(keys)
            self.proc_left_click()
            self.proc_right_click()
            return

        if keys[pg.K_p]:
            self.pause_music = not self.pause_music
            self.pause() if self.pause_music else self.play((self.current_ms / 1000))
        if self.playing:
            self.current_ms = (
                time.time() - self.play_ts
            ) * 1000 + self.begin_playing_ms
        self.update_lane_alpha_values()
        self.proc_key_presses(keys)
        self.acc_status.update()

    def draw_sidelines_deco(self):
        pg.draw.line(self.bg_surface, "white", [0, 0], [0, WIN_HEIGHT])
        pg.draw.line(self.bg_surface, "white", [79, 0], [79, WIN_HEIGHT])

    def draw_hud_bg(self):
        self.bg_surface.fill("black")
        self.bg_surface.set_alpha(130)
        if self.editor:
            self.bg_surface.set_alpha(255)

        for idx, lane in enumerate(self.lane_surfaces):
            self.bg_surface.blit(lane, [idx * 20, 0])
        self.draw_sidelines_deco()
        self.game.screen.blit(self.bg_surface, [10, 0])

    def draw_static_arrows(self):
        for idx, (arrow, arrow_tinted) in enumerate(
            zip(self.static_arrows, self.falling_arrows)
        ):
            self.game.screen.blit(arrow, [10 + idx * 20, 10])

    def draw_help_lines(self, deg=8, color=None):
        if color is None:
            color = [100, 100, 100]
        idx = 0
        ms_per_hit = (60000 / 8) * deg / self.bpm

        while True:
            y_pos = ms_per_hit * idx - self.current_ms % ms_per_hit
            pg.draw.rect(
                self.game.screen,
                color,
                [10, 20 + (y_pos / self.fall_speed), self.bg_surface.get_width(), 1],
            )
            if y_pos + 10 > 1000:
                break
            idx += 1

    def draw_falling_arrows(self):
        viewport = WIN_HEIGHT - 10
        if self.editor:
            for lane_idx, lane in enumerate(self.editor_lanes):
                for ts_idx, timestamp in enumerate(lane):
                    timestamp = timestamp

                    arrow_position = (timestamp - self.current_ms) / self.fall_speed
                    if arrow_position > viewport + 10:
                        continue

                    self.game.screen.blit(
                        self.falling_arrows[lane_idx],
                        [10 + lane_idx * 20, 10 + arrow_position],
                    )
        else:
            for lane_idx, lane in enumerate(self.lanes):
                for ts_idx, timestamp in enumerate(lane):
                    timestamp = timestamp

                    arrow_position = (timestamp - self.current_ms) / self.fall_speed
                    if arrow_position > viewport + 10:
                        continue

                    if arrow_position < -20:
                        self.acc_status.current_status = 4
                        self.acc_status.fire_anim()
                        self.misses += 1
                        self.lanes[lane_idx].pop(ts_idx)

                    else:
                        self.game.screen.blit(
                            self.falling_arrows[lane_idx],
                            [10 + lane_idx * 20, 10 + arrow_position],
                        )

    def draw_hover_ts(self):
        mouse = pg.mouse.get_pos()
        y = mouse[1]
        hover_ts = self.current_ms + (y - 20) * self.fall_speed
        current_ts = self.game.ariel_font.render(
            f"{hover_ts:.0f}ms", False, "white", "black"
        )
        ts_rect = current_ts.get_rect(left=0, bottom=y)
        if pg.Rect(10, 0, *self.bg_surface.get_size()).collidepoint(mouse):
            self.game.screen.blit(current_ts, ts_rect)

    def draw_time_controls(self):
        pg.draw.rect(self.game.screen, "black", self.time_controls_rect, 0)
        for idx, value in enumerate(self.editor_beat_data):
            rect = self.time_controls_rect.copy()
            rect.height = 1
            rect.width = self.time_controls_rect.width * value / self.max_beat
            rect.top = idx
            rect.centerx = self.time_controls_rect.centerx
            pg.draw.rect(self.game.screen, "red", rect, 0)
        actual_pos = self.time_controls_rect.copy()
        actual_pos.height = 1
        actual_pos.top = WIN_HEIGHT * (self.current_ms / (self.music_length * 1000))
        pg.draw.rect(self.game.screen, "blue", actual_pos, 0)

        idk_what_to_name_this = actual_pos.copy()
        idk_what_to_name_this.left = 0
        idk_what_to_name_this.top = pg.mouse.get_pos()[1]
        idk_what_to_name_this.width = WIN_WIDTH

        pg.draw.rect(self.game.screen, "orange", idk_what_to_name_this, 0)

    def draw_wave_data(self):
        pg.draw.rect(self.game.screen, "black", self.wave_data_rect, 0)
        for i in range(-50 * self.fall_speed, 500 * self.fall_speed):
            rect = self.wave_data_rect.copy()
            rect.top = 20 + int(i / self.fall_speed)
            rect.height = 1
            rect.width = (
                self.wave_data_rect.width
                * self.music_analyzer.beat_idx_ms(self.current_ms + i)
                / self.max_beat
            )
            rect.centerx = self.wave_data_rect.centerx

            pg.draw.rect(
                self.game.screen,
                "orange",
                rect,
                0,
            )

    def draw(self):
        self.draw_hud_bg()
        self.draw_static_arrows()
        if self.editor:
            self.draw_time_controls()
            self.draw_wave_data()
            self.draw_help_lines(deg=2)
            self.draw_falling_arrows()
            self.draw_hover_ts()
            pg.draw.line(self.game.screen, "red", [0, 20], [WIN_WIDTH, 20], 1)
            return
        self.draw_falling_arrows()
        self.acc_status.draw()
