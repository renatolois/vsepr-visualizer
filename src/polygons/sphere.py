import math
import glm
from typing import List, NamedTuple

from vertex import Vertex
from mesh import Mesh
from shader import Shader
from material import Material
from model import Model
from entity import Entity
from transform import Transform
from renderer import Renderer
from camera import Camera
from light import Light


class VerticesAndIndicesPointers(NamedTuple):
    vertices: List[Vertex]
    indices: List[int]


def num_lat_lines(lat_level: int) -> int:
    return 3 * round(pow(2, lat_level - 1)) - 1


def x_lat_coord(
        single_lat_angle: float,
        lat_angle_offset: float,
        pos: int,
        radius: float
) -> float:
    return math.cos(lat_angle_offset + single_lat_angle * pos) * radius


def x_lon_coord(
        single_lon_angle: float,
        lon_angle_offset: float,
        pos: int,
        radius: float
) -> float:
    return x_lat_coord(single_lon_angle, lon_angle_offset, pos, radius)


def y_lat_coord(
        single_lat_angle: float,
        lat_angle_offset: float,
        pos: int,
        radius: float
) -> float:
    return math.sin(lat_angle_offset + single_lat_angle * pos) * radius


def z_lon_coord(
        single_lon_angle: float,
        lon_angle_offset: float,
        pos: int,
        radius: float
) -> float:
    return y_lat_coord(single_lon_angle, lon_angle_offset, pos, radius)


def num_lon_rings(lon_level: int) -> int:
    return round(pow(2, lon_level))


def get_sphere_vertices_and_indices(
        lat_level: int,
        lon_level: int,
        radius: float
) -> VerticesAndIndicesPointers:
    lat_lines = num_lat_lines(lat_level)
    lat_sides = lat_lines + 1

    single_lat_angle = math.pi / float(lat_sides)

    lon_sides = num_lon_rings(lon_level) * 2
    lon_lines = lon_sides

    single_lon_angle = 2 * math.pi / lon_sides

    sphere_vertices: List[Vertex] = []

    for i in range(1, lon_sides + 1):
        x_tex_coord = (single_lon_angle * i) / (math.pi * 2)
        y_tex_coord = 1.0
        north_vertice = Vertex(
            position=glm.vec3(0.0, radius, 0.0),
            normal=glm.vec3(0.0, 1.0, 0.0),
            tex_coords=glm.vec2(x_tex_coord, y_tex_coord)
        )
        sphere_vertices.append(north_vertice)

    for i in range(1, lat_lines + 1):
        y = y_lat_coord(single_lat_angle, math.pi / 2, i, radius)
        sub_circle_radius = abs(
            math.cos(math.pi / 2.0 + single_lat_angle * i) * radius)

        for j in range(1, lon_lines + 1):
            z = z_lon_coord(single_lon_angle, 0, j, sub_circle_radius)
            x = x_lon_coord(single_lon_angle, 0, j, sub_circle_radius)

            x_normal = x / radius
            y_normal = y / radius
            z_normal = z / radius

            x_tex_coord = (single_lon_angle * j) / (math.pi * 2)
            y_tex_coord = (single_lat_angle * i) / math.pi

            sphere_vertices.append(
                Vertex(
                    position=glm.vec3(x, y, z),
                    normal=glm.vec3(x_normal, y_normal, z_normal),
                    tex_coords=glm.vec2(x_tex_coord, y_tex_coord)
                )
            )

    for i in range(1, lon_sides + 1):
        x_tex_coord = (single_lon_angle * i) / (math.pi * 2)
        y_tex_coord = 0.0
        south_vertice = Vertex(
            position=glm.vec3(0.0, -radius, 0.0),
            normal=glm.vec3(0.0, -1.0, 0.0),
            tex_coords=glm.vec2(x_tex_coord, y_tex_coord)
        )
        sphere_vertices.append(south_vertice)

    sphere_indices: List[int] = []

    for i in range(lon_lines):
        sphere_indices.append(i)
        sphere_indices.append(i + lon_lines)
        sphere_indices.append((i + 1) % lon_lines + lon_lines)

    for i in range(1, lat_lines):
        for j in range(lon_lines):
            sphere_indices.append(i * lon_lines + j)
            sphere_indices.append((i + 1) * lon_lines + j)
            sphere_indices.append((i + 1) * lon_lines + (j + 1) % lon_lines)

            sphere_indices.append(i * lon_lines + j)
            sphere_indices.append((i + 1) * lon_lines + (j + 1) % lon_lines)
            sphere_indices.append(i * lon_lines + (j + 1) % lon_lines)

    for i in range(lon_lines):
        sphere_indices.append(i + lat_sides * lon_lines)
        sphere_indices.append(((i + 1) % lon_lines) +
                              (lat_sides - 1) * lon_lines)
        sphere_indices.append(i + (lat_sides - 1) * lon_lines)

    return VerticesAndIndicesPointers(sphere_vertices, sphere_indices)


class Sphere:
    def __init__(
            self,
            radius: float,
            lat_level: int,
            lon_level: int,
            sphere_color: glm.vec4 = glm.vec4(1.0, 0.0, 0.0, 1.0)
    ):
        sphere_vertices, sphere_indices = get_sphere_vertices_and_indices(
            lat_level, lon_level, radius)

        sphere_transform = Transform(
            glm.vec3(0.0, 0.0, 0.0),
            glm.quat(1.0, 0.0, 0.0, 0.0),
            glm.vec3(1.0, 1.0, 1.0)
        )

        sphere_mesh = Mesh(sphere_vertices, sphere_indices)

        sphere_shader = Shader("src/shaders/polygon.vert",
                               "src/shaders/polygon.frag")

        sphere_material = Material(
            sphere_shader,
            glm.vec4(0.5, 0.5, 0.9, 1.0)
        )
        sphere_material.set_color(sphere_color)

        sphere_model = Model(
            [sphere_mesh],
            [sphere_material],
            [sphere_transform]
        )

        self.sphere_entity = Entity(sphere_model, sphere_transform)

    def get_transform(self) -> Transform:
        return self.sphere_entity.get_transform()

    def set_transform(self, transform: Transform) -> None:
        self.sphere_entity.set_transform(transform)

    def get_color(self) -> glm.vec4:
        model_piece_vector = self.sphere_entity.get_model().get_model_pieces()
        if len(model_piece_vector) != 1:
            print("Sphere entity->model->model_pieces_vector must have a size of 1, but it doesn't.")  # noqa: E201
            exit(1)
        return model_piece_vector[0].material.get_color()

    def set_color(self, color: glm.vec4) -> None:
        model_piece_vector = self.sphere_entity.get_model().get_model_pieces()
        if len(model_piece_vector) != 1:
            print("Sphere entity->model->model_pieces_vector must have a size of 1, but it doesn't.")  # noqa: E201
            exit(1)
        model_piece_vector[0].material.set_color(color)

    def render(self, renderer: Renderer, camera: Camera, light: Light) -> None:
        renderer.render_entity(camera, self.sphere_entity, light)
