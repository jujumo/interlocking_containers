import numpy as np
import trimesh
from trimesh.transformations import translation_matrix, rotation_matrix, scale_matrix, scale_and_translate
from jsonargparse import CLI
from importlib import resources
from pathlib import Path
from functools import lru_cache


@lru_cache(maxsize=3)
def load_model_cache(
        hollow: int = 0,
        verbosity: int = 1
):
    """ returns the model from the installed package data/ """
    model_name = 'model' if hollow == 0 else f'model_hollow{hollow:1}'
    resource = resources.files('interlocking_containers').joinpath(f'data/{model_name}.stl')

    # If we're running from source or editable install, this is already a Path
    mesh = None
    if isinstance(resource, Path):
        model_path = resource
        mesh = trimesh.load(model_path)

    if mesh is None:
        # Otherwise extract to a temporary location
        with resources.as_file(resource) as model_path:
            mesh = trimesh.load(model_path)
    return mesh


def create_box_size(
        nx: int = 3,
        ny: int = 3,
        height_mm: float = 40.,
        hollow: int = 0,
        scale: float = 1.0,
        verbosity: int = 1
):

    if nx < 3:
        print(f'warning: nx must be >= 3 ({nx=}). Will be ignored.')
    if ny < 3:
        print(f'warning: ny must be >= 3 ({ny=}). Will be ignored.')
    if height_mm < 40.:
        print(f'warning: height_mm must be >= 40 ({height_mm=}). Will be ignored.')

    mesh = load_model_cache(hollow=hollow).copy()  # make a copy, to avoid modifying the cached version.

    nx = max(nx, 3)
    ny = max(ny, 3)
    height_mm = max(height_mm, 40.0)

    axes = {
        'x': np.array([1, 0, 0]),
        'y': np.array([0, 1, 0]),
        'z': np.array([0, 0, 1]),
    }

    # make Z-UP for ease of mind
    mesh.apply_transform(rotation_matrix(np.pi/2., axes['x']))

    # notch creation : from abc to abbbbc
    notch_width = 10.
    notch_repeat = {
        'x': nx,
        'y': ny
    }

    for axis_id in ['x', 'y']:
        ## slice_plane produce degenerate cases and lead to non water-tight volumes
        axis = axes[axis_id]
        nb_notch = notch_repeat[axis_id]
        axis_mask = axis.astype(bool)
        bound_beg = np.array(mesh.bounds)
        bound_mid = np.array(mesh.bounds)
        bound_end = np.array(mesh.bounds)
        bound_beg[1][axis_mask] = -notch_width/2
        bound_mid[0][axis_mask] = -notch_width/2
        bound_mid[1][axis_mask] = +notch_width/2
        bound_end[0][axis_mask] = +notch_width/2
        box_beg = trimesh.creation.box(bounds=bound_beg)
        box_mid = trimesh.creation.box(bounds=bound_mid)
        box_end = trimesh.creation.box(bounds=bound_end)
        mesh_beg = trimesh.boolean.intersection([mesh, box_beg])
        mesh_mid = trimesh.boolean.intersection([mesh, box_mid])
        mesh_end = trimesh.boolean.intersection([mesh, box_end])
        assert mesh_beg.is_volume and mesh_mid.is_volume and mesh_end.is_volume

        translation = translation_matrix(axis * -notch_width)
        notches = []
        for idx_notch in range(1, nb_notch-1):
            new_notch = mesh_mid.copy()
            translation[0:3, 3] = translation[0:3, 3] + np.array([axis * notch_width])
            new_notch.apply_transform(translation)
            notches.append(new_notch)

        mesh_end.apply_transform(translation)
        mesh_parts = [mesh_beg] + notches + [mesh_end]
        mesh = trimesh.boolean.union(mesh_parts)

    # vertical elongation
    height_min = 40.0
    slice_height = 1.0
    if height_mm > height_min:
        vertical = axes['z']
        vertical_mask = vertical.astype(bool)
        bound_bot = np.array(mesh.bounds)
        bound_ctr = np.array(mesh.bounds)
        bound_top = np.array(mesh.bounds)
        bound_bot[1][vertical_mask] = -slice_height/2
        bound_ctr[0][vertical_mask] = -slice_height/2
        bound_ctr[1][vertical_mask] = +slice_height/2
        bound_top[0][vertical_mask] = +slice_height/2
        box_bot = trimesh.creation.box(bounds=bound_bot)
        box_ctr = trimesh.creation.box(bounds=bound_ctr)
        box_top = trimesh.creation.box(bounds=bound_top)
        mesh_bot = trimesh.boolean.intersection([mesh, box_bot])
        mesh_ctr = trimesh.boolean.intersection([mesh, box_ctr])
        mesh_top = trimesh.boolean.intersection([mesh, box_top])
        assert mesh_bot.is_volume and mesh_ctr.is_volume and mesh_top.is_volume

        # from 40.0 to height = increase
        # so, I get a slice in the middle of size slice_height,
        # and scale it up to slice_height+increase.
        increase = height_mm - height_min
        mid_scale = np.ones(3)
        mid_scale[vertical_mask] = ((increase + slice_height) / slice_height)
        mid_trans = vertical * increase / 2.
        mid_mat = scale_and_translate(mid_scale, mid_trans)
        mesh_ctr.apply_transform(mid_mat)
        mesh_top.apply_transform(translation_matrix(vertical * increase))
        # reassemble
        mesh_parts = [mesh_bot, mesh_ctr, mesh_top]
        mesh = trimesh.boolean.union(mesh_parts)

    # global scale
    s_mat = np.diag([scale, scale, scale, 1])
    mesh.apply_transform(s_mat)

    return mesh


def save_box_size(
        output: str = '',
        nx: int = 3,
        ny: int = 3,
        height: float = 40.,
        hollow: int = 0,
        scale: float = 1.0,
        up: str = 'z',
        verbosity: int = 1,
):
    if not output:
        output = f'stackable_x{nx:02}y{ny:02}z{int(height):03}t{hollow:1}s{scale}u{up}.stl'

    if up.lower() not in ['x', 'y', 'z']:
        print(f'warning: up must be x, y or z ({up=}). Will be ignored.')

    mesh = create_box_size(nx=nx, ny=ny, height_mm=height, hollow=hollow, scale=scale, verbosity=verbosity)

    if verbosity >= 2:
        mesh.show()

    if up.lower() == 'y':
        mesh.apply_transform(rotation_matrix(-np.pi / 2., [1, 0, 0]))
    if up.lower() == 'x':
        mesh.apply_transform(rotation_matrix(-np.pi / 2., [0, 1, 0]))

    if verbosity >= 1:
        print(f'exporting "{output}".')
    mesh.export(output)


def create_box():
    CLI(save_box_size)


if __name__ == '__main__':
    create_box()


