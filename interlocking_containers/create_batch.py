import os

import numpy as np
from jsonargparse import CLI
from interlocking_containers.create_box import save_box_size
from rich.progress import track
import os.path as path
from dataclasses import dataclass


@dataclass
class BoxConfig:
    nx: int = 3
    ny: int = 3
    height: float = 40.
    scale: float = 1.0
    fill: int = 0
    up: str = 'z'


def create_batch_box(
        output_dir: str = 'models',
        up: str = 'z',
        force: bool = False,
        verbosity: int = 1
):
    """
    Save a 3D box model.

    Args:
        output_dir: Output root directory.
        up: Up direction axis (x, y, or z).
        force: is True, force rewrite existing files.
        verbosity: Verbosity level (0 = quiet, 1 = display progress, 2 = warnings+export files, 3 = show meshes).
    """
    interesting_notch_number = [4, 5, 6, 7, 8, 9, 10, 12, 16]
    interesting_height = [40., 50]
    interesting_fill = [0, 2]

    configs = [
        BoxConfig(nx=nx, ny=ny, height=height, fill=fill, up=up)
        for fill in interesting_fill
        for height in interesting_height
        for nx in interesting_notch_number
        for ny in interesting_notch_number
    ]

    for config in track(configs):
        fill_name = 'solid' if config.fill == 0 else f'hollow{config.fill}'
        height_name = f'height{int(config.height):03}'
        subdir_path = path.join(output_dir, fill_name)
        os.makedirs(subdir_path, exist_ok=True)

        output_filename = f'container_{fill_name}_H{int(config.height):03}_X{config.nx:02}_Y{config.ny:02}.stl'
        output_filepath = subdir_path + '/' + output_filename
        if path.isfile(output_filepath) and not force:
            if verbosity >= 1:
                print(f'skip already existing {output_filepath}.')
            continue
        try:
            save_box_size(
                output=output_filepath,
                nx=config.nx,
                ny=config.ny,
                height=config.height,
                fill=config.fill,
                verbosity=verbosity-1
            )
        except Exception:
            print(f'fail to save {output_filepath}.')


def create_batch():
    CLI(create_batch_box)


if __name__ == '__main__':
    create_batch()


