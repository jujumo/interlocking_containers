import os

import numpy as np
from jsonargparse import CLI
from interlocking_containers.create_box import save_box_size
from rich.progress import track
import os.path as path


def batch_create_box(
        output_dir: str = 'models',
        force: bool =False,
        verbosity: int = 1
):
    interesting_notch_number = [3, 4, 5, 6, 8, 10, 12, 16, 32]
    interesting_height = [40., 50, 80, 100]
    nx, ny, height, scale, hollow = 3, 3, 40, 1.0, 0
    for scale in [1.0, 2.0]:
        subdir_scale_name = f'scale{int(scale):1}'
        for hollow in [0, 2]:
            subdir_hollow_name = 'solid' if hollow == 0 else 'hollow'
            subdir_path = output_dir + '/' + subdir_scale_name + '/' + subdir_hollow_name
            os.makedirs(subdir_path, exist_ok=True)
            for nx in track(interesting_notch_number):
                for ny in track(interesting_notch_number):
                    for height in interesting_height:
                        output_filename = (f'stackable_{subdir_scale_name}_{subdir_hollow_name}'
                                           f'_h{int(height):03}_x{nx:02}_y{ny:02}.stl')
                        output_filepath = subdir_path + '/' + output_filename
                        if path.isfile(output_filepath) and not force:
                            if verbosity >= 1:
                                print(f'skip already existing {output_filepath}.')
                            continue

                        try:
                            save_box_size(
                                output=output_filepath,
                                nx=nx,
                                ny=ny,
                                height=height,
                                scale=scale,
                                verbosity=verbosity-1
                            )
                        except ValueError:
                            print(f'fail to save {output_filepath}.')


def batch_create():
    CLI(batch_create_box)


if __name__ == '__main__':
    batch_create()


