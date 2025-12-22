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
    hollow: int = 0
    up: str = 'z'


def create_batch_box(
        output_dir: str = 'models',
        up: str = 'z',
        scale: float = 1.0,
        hollow: bool = False,
        force: bool = False,
        verbosity: int = 1
):
    """
    Save a 3D box model.

    Args:
        output_dir: Output root directory.
        up: Up direction axis (x, y, or z).
        scale: Scaling factor applied to the model.
        hollow: If true then the hollow version is done.
        force: is True, force rewrite existing files.
        verbosity: Verbosity level (0 = quiet, 1 = display progress, 2 = warnings+export files, 3 = show meshes).
    """
    interesting_notch_number = [3, 4, 5, 6, 8, 9, 10, 12, 16]
    interesting_height = [40., 60]
    interesting_hollow = [0]
    if hollow:
        interesting_hollow.append(1)
    configs = [
        BoxConfig(nx=nx, ny=ny, height=height, hollow=hollow, up=up, scale=scale)
        for hollow in interesting_hollow
        for height in interesting_height
        for nx in interesting_notch_number
        for ny in interesting_notch_number
    ]

    for config in track(configs):
        hollow_name = 'solid' if config.hollow == 0 else 'hollow'
        height_name = f'height{int(config.height):03}'
        subdir_path = path.join(output_dir, hollow_name, height_name)
        os.makedirs(subdir_path, exist_ok=True)

        output_filename = f'container_{hollow_name}_h{int(config.height):03}_x{config.nx:02}_y{config.ny:02}.stl'
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
                hollow=config.hollow,
                verbosity=verbosity-1
            )
        except Exception:
            print(f'fail to save {output_filepath}.')


def create_batch():
    CLI(create_batch_box)


if __name__ == '__main__':
    create_batch()


