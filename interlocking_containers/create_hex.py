import numpy as np
import trimesh
from trimesh.transformations import translation_matrix, rotation_matrix, scale_and_translate
from jsonargparse import CLI, ArgumentParser, SUPPRESS
from importlib import resources
from pathlib import Path
from functools import lru_cache
from typing import Optional
from shapely.geometry import Polygon


axes = {
    'x': np.array([1, 0, 0]),
    'y': np.array([0, 1, 0]),
    'z': np.array([0, 0, 1]),
}

@lru_cache(maxsize=3)
def load_model_cache(
        fill: int = 0,
        verbosity: int = 1
):
    """ returns the model from the installed package data/ """
    model_name = 'honeycomb' if fill == 0 else f'honeycomb_hollow{fill:1}'
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


def create_hex_size(
        n: int = 4,
        height_mm: float = 40.,
        fill: int = 0,
        scale: float = 1.0,
        verbosity: int = 1
):
    if n < 2 and verbosity >= 1:
        print(f'warning: n must be >= 2 ({n=}). Will be ignored.')
    if height_mm < 40. and verbosity >= 1:
        print(f'warning: height_mm must be >= 40 ({height_mm=}). Will be ignored.')
    if fill < 0 and verbosity >= 1:
        print(f'warning: fill must be >= 0 ({fill=}). Will be ignored.')

    n = max(n, 2)
    height_mm = max(height_mm, 40.0)
    fill = int(max(fill, 0))

    hex3_mesh = load_model_cache(fill=fill).copy()  # make a copy, to avoid modifying the cached version.

    # make Z-UP for ease of mind
    hex3_mesh.apply_transform(rotation_matrix(np.pi/2., axes['x']))
    original_cake_mesh = hex3_mesh.copy()
    # scene = trimesh.Scene()  # for debug
    # notch creation : from abc to abbbbc
    notch_width = 10.
    notch_depth = 10.
    hex3_bounds = np.array(hex3_mesh.bounds)
    hex3_size = hex3_bounds[1][:] - hex3_bounds[0][:]
    radius = 50
    slice_of_cake_vertices = [[0, 0]]
    for angle in [60, 120]:
        rad = np.deg2rad(angle)
        slice_of_cake_vertices.append([np.cos(rad), np.sin(rad)])
    slice_of_cake_vertices = np.array(slice_of_cake_vertices)
    slice_of_cake_vertices *= radius
    # Extrude the polygon along the z-axis
    cut_slice_of_cake_mesh = trimesh.creation.extrude_polygon(Polygon(slice_of_cake_vertices), hex3_size[2])
    cut_slice_of_cake_mesh.apply_transform(translation_matrix((0, 0, -hex3_size[2]/2)))
    rotation60 = rotation_matrix(np.deg2rad(60), axes['z'])
    template_slices = []
    for cut in range(2):
        slice_of_cake_mesh = trimesh.boolean.intersection([original_cake_mesh, cut_slice_of_cake_mesh])
        slice_bounds = np.array(slice_of_cake_mesh.bounds)

        """
        Partition the slice in 4 pieces.
                 0
        xa      xb  |   xc      xd
        ╔═══════╦═══════╦═══════╗yc
        ║   A   ║   B   ║   C   ║    
        ╠═══════╩═══════╩═══════╣yb
        ║         CORE          ║
        ╚═══════════════════════╝ya__0    
        """
        # pieces_of_slice = slice_bounds[np.newaxis, ...].repeat(4, axis=0)
        xa = slice_bounds[0, 0]
        xd = slice_bounds[1, 0]
        xb = -notch_width / 2.
        xc = -xb
        ya = slice_bounds[0, 1]
        yc = slice_bounds[1, 1]
        yb = yc - notch_depth
        za = slice_bounds[0, 2]
        zb = slice_bounds[1, 2]
        parts_of_slice_bounds = [
            [[xa, yb, za], [xb, yc, zb]],
            [[xb, yb, za], [xc, yc, zb]],
            [[xc, yb, za], [xd, yc, zb]],
            [[xa, ya, za], [xd, yb, zb]],
        ]

        parts_mesh = []
        for piece_of_slice_bounds in parts_of_slice_bounds:
            cut_part_mesh = trimesh.creation.box(bounds=piece_of_slice_bounds)
            part_mesh = trimesh.boolean.intersection([cut_part_mesh, slice_of_cake_mesh])
            parts_mesh.append(part_mesh)
            # scene.add_geometry(part_mesh)


        """
        Now re-assemble
           xa'     xb'         0           xc'     xd'
           ╔═══════╦═══════╦═══════╦═══════╦═══════╗    yc'
           ║   A   ║   B   ║   B   ║   B   ║   C   ║   notch_depth
        ╔══╩═══════╩═══════╩═══════╩═══════╩═══════╩══╗ yb'
        ║  |<------------------N------------------>|  ║
        ║  |                                       |  ║
        ║  |              Core' = f * Core         |  ║
        ║  |                                       |  ║
        ║  |                                       |  ║
        ╚═════════════════════════════════════════════╝ ya' __0    
        """

        xy_factor = np.sin(np.deg2rad(60))
        nb_notch_to_add = n - 3
        width_increase = notch_width * nb_notch_to_add
        depth_shift = width_increase * xy_factor
        core_scale = (yb+depth_shift) / yb
        parts_mesh[0].apply_transform(translation_matrix((-nb_notch_to_add*notch_width/2., depth_shift, 0)))
        parts_mesh[2].apply_transform(translation_matrix((+nb_notch_to_add*notch_width/2., depth_shift, 0)))
        parts_mesh[3].apply_transform(scale_and_translate(scale=(core_scale, core_scale, 1)))

        notch_mesh = parts_mesh.pop(1)
        notch_mesh.apply_transform(translation_matrix((-nb_notch_to_add*notch_width/2., depth_shift, 0)))
        for i in range(n-2):
            parts_mesh.append(notch_mesh.copy())
            notch_mesh.apply_transform(translation_matrix((notch_width, 0, 0)))

        # for part_mesh in parts_mesh:
        #     scene.add_geometry(part_mesh)
        template_slice = trimesh.boolean.union(parts_mesh)
        template_slices.append(template_slice)
        original_cake_mesh.apply_transform(rotation60)

    # then rebuild a vake with all slices
    reassemble_cake_mesh = template_slices[0].copy()
    for cut in range(1, 6):
        reassemble_cake_mesh.apply_transform(rotation60)
        reassemble_cake_mesh = trimesh.boolean.union([reassemble_cake_mesh, template_slices[cut % 2]])
    # scene.add_geometry(reassemble_cake_mesh)
    # scene.show() ; exit()

    # vertical elongation
    height_min = 40.0
    slice_height = 1.0
    if height_mm > height_min:
        vertical = axes['z']
        vertical_mask = vertical.astype(bool)
        bound_bot = np.array(reassemble_cake_mesh.bounds)
        bound_ctr = np.array(reassemble_cake_mesh.bounds)
        bound_top = np.array(reassemble_cake_mesh.bounds)
        bound_bot[1][vertical_mask] = -slice_height/2
        bound_ctr[0][vertical_mask] = -slice_height/2
        bound_ctr[1][vertical_mask] = +slice_height/2
        bound_top[0][vertical_mask] = +slice_height/2
        box_bot = trimesh.creation.box(bounds=bound_bot)
        box_ctr = trimesh.creation.box(bounds=bound_ctr)
        box_top = trimesh.creation.box(bounds=bound_top)
        # scene.add_geometry(box_ctr)
        # scene.add_geometry(reassemble_cake_mesh)
        # scene.show()
        # exit()
        mesh_bot = trimesh.boolean.intersection([reassemble_cake_mesh, box_bot])
        mesh_ctr = trimesh.boolean.intersection([reassemble_cake_mesh, box_ctr])
        mesh_top = trimesh.boolean.intersection([reassemble_cake_mesh, box_top])
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
        reassemble_cake_mesh = trimesh.boolean.union(mesh_parts)

    # global scale
    if scale != 1.0:
        s_mat = np.diag([scale, scale, scale, 1])
        reassemble_cake_mesh.apply_transform(s_mat)

    return reassemble_cake_mesh


def save_hex_size(
        output: str = 'honeycomb.stl',
        n: int = 4,
        height: float = 40.0,
        fill: int = 0,
        scale: float = 1.0,
        up: str = 'z',
        verbosity: int = 1,
):
    """
    Save a 3D box model.

    Args:
        output: Output STL filename.
        n: Number of notches along biggest axis.
        height: Height of the box in millimeters.
        fill: Whether the box is hollow (0 = solid, 1,2,3 = hollow).
        scale: Scaling factor applied to the model.
        up: Up direction axis (x, y, or z).
        verbosity: Verbosity level (0 = quiet, 1 = show warnings+export, 2 = show mesh).
    """
    if up.lower() not in ['x', 'y', 'z']:
        print(f'warning: up must be x, y or z ({up=}). Will be ignored.')

    mesh = create_hex_size(n=n, height_mm=height, fill=fill, scale=scale, verbosity=verbosity)

    if verbosity >= 2:
        mesh.show()

    if up.lower() == 'y':
        mesh.apply_transform(rotation_matrix(-np.pi / 2., [1, 0, 0]))
    if up.lower() == 'x':
        mesh.apply_transform(rotation_matrix(-np.pi / 2., [0, 1, 0]))

    if output != '':
        if verbosity >= 1:
            print(f'exporting "{output}".')
        mesh.export(output)


def create_hex():
    parser = ArgumentParser()
    # Automatically add all arguments from greetings parameters
    parser.add_function_arguments(save_hex_size)
    parser.add_argument('-o', default=SUPPRESS, dest='output')
    parser.add_argument('-n', default=SUPPRESS, dest='n')
    parser.add_argument('-t', default=SUPPRESS, dest='height')
    parser.add_argument('-s', default=SUPPRESS, dest='scale')
    parser.add_argument('-f', default=SUPPRESS, dest='fill')
    parser.add_argument('-u', default=SUPPRESS, dest='up')
    parser.add_argument('-v', default=SUPPRESS, dest='verbosity')
    args = parser.parse_args()

    save_hex_size(**vars(args))


if __name__ == '__main__':
    create_hex()


