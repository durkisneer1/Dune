import inspect
import os
from typing import TYPE_CHECKING

import pygame as pg

from src.core.settings import *
from src.tile import Tile

if TYPE_CHECKING:
    from pytmx import TiledMap

    from main import Game


image_load = pg.image.load
pg_surface = pg.Surface


def import_folder(
    path: str,
    is_alpha: bool = True,
    scale: float = 1,
    highlight: bool = False,
    blur: bool = False,
) -> list[pg.Surface]:
    surf_list = []
    for _, __, img_file in os.walk(path):
        for image in img_file:
            full_path = path + "/" + image
            surface = import_image(full_path, is_alpha, scale, highlight, blur)
            surf_list.append(surface)
    return surf_list


def import_image(
    path: str,
    is_alpha: bool = True,
    scale: float = 1,
    highlight: bool = False,
    blur: bool = False,
) -> pg.Surface:
    image_surf = (
        pg.image.load(path).convert_alpha()
        if is_alpha
        else pg.image.load(path).convert()
    )

    if scale != 1 and scale > 0:
        image_surf = pg.transform.scale_by(image_surf, scale)
    if highlight:
        image_surf.fill((40, 40, 40, 0), special_flags=pg.BLEND_RGB_ADD)
    if blur:
        template_surf = pg.Surface(
            (image_surf.get_width() + 20, image_surf.get_height() + 20), pg.SRCALPHA
        )
        template_surf.fill((0, 0, 0, 0))
        image_rect = image_surf.get_frect(
            center=(template_surf.get_width() / 2, template_surf.get_height() / 2)
        )
        template_surf.blit(image_surf, image_rect)
        image_surf = pg.transform.gaussian_blur(template_surf, 5)

    return image_surf


def load_tmx_layers(
    game: "Game",
    data: "TiledMap",
    layer_name: str,
    targets: tuple[list, ...] | list,
    tile_offset: int = 0,
) -> None:
    if isinstance(targets, tuple) and not targets:
        return

    layer_names = [
        layer.name for layer in data.visible_layers if hasattr(layer, "data")
    ]
    if layer_name not in layer_names:
        print(f"ERROR: Layer '{layer_name}' not found in '{data.filename}'")
        return

    for layer in data.visible_layers:
        if hasattr(layer, "data"):
            if layer.name == layer_name:
                for x, y, surface in layer.tiles():
                    pos = pg.Vector2(
                        x * TILE_WIDTH, y * TILE_HEIGHT - tile_offset * TILE_HEIGHT
                    )
                    tile = Tile(game, pos, surface, layer.name)
                    if isinstance(targets, list):
                        targets.append(tile)
                    else:
                        for target in targets:
                            target.append(tile)


def new_image_load(*args, **kwargs):
    print("Image loaded:", args[0])
    return image_load(*args, **kwargs)


def new_surface(*args, **kwargs):
    calling_file = inspect.currentframe().f_back.f_globals["__file__"]
    calling_file = os.path.basename(calling_file)
    print(f"Surface created in {calling_file}")
    return pg_surface(*args, **kwargs)


pg.image.load = new_image_load
pg.Surface = new_surface
