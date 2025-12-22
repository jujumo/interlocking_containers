import os

import numpy as np
from jsonargparse import CLI
from interlocking_containers.create_box import save_box_size
from rich.progress import Progress
import os.path as path


def create_batch_box(
        output_dir: str = 'models',
        force: bool = False,
        verbosity: int = 1
):
    interesting_notch_number = [3, 4, 5, 6, 8, 10, 12, 16, 32]
    interesting_height = [40., 50, 100]
    interesting_scale = [1.0, 2.0]
    interesting_hollow = [0, 2]
    # default value, in case you need
    nx, ny, height, scale, hollow = 3, 3, 40, 1.0, 0
    total_number_of_models = (
            len(interesting_notch_number) *
            len(interesting_notch_number) *
            len(interesting_height) *
            len(interesting_scale) *
            len(interesting_hollow) *
            1
    )

    with Progress() as progress:
        progress_bar = progress.add_task("[cyan]creating...", total=total_number_of_models)
        for scale in [1.0, 2.0]:
            subdir_scale_name = f'scale{int(scale):1}'
            for hollow in [0, 2]:
                subdir_hollow_name = 'solid' if hollow == 0 else 'hollow'
                for height in interesting_height:
                    subdir_height_name = f'height{int(height):03}'
                    subdir_path = path.join(output_dir, subdir_scale_name, subdir_hollow_name, subdir_height_name)
                    os.makedirs(subdir_path, exist_ok=True)
                    for nx in interesting_notch_number:
                        for ny in interesting_notch_number:
                                progress.update(progress_bar, advance=1.0)
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
                                except Exception:
                                    print(f'fail to save {output_filepath}.')


def create_batch():
    CLI(create_batch_box)


if __name__ == '__main__':
    create_batch()


