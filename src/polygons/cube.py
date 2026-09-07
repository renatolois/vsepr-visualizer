import glm
from typing import List
from vertex import Vertex
from mesh import Mesh
from shader import Shader
from material import Material
from model import Model
from entity import Entity
from transform import Transform
from camera import Camera
from light import Light
from renderer import Renderer


class Cube:
    def __init__(self, size_factor: float):
        s = size_factor
        half = s * 0.5

        cube_vertices: List[Vertex] = [
            Vertex(
                glm.vec3(half,  half,  half),
                glm.vec3(0,  1,  0),
                glm.vec2(0, 0)
            ),
            Vertex(
                glm.vec3(half,  half, -half),
                glm.vec3(0,  1,  0),
                glm.vec2(0, 0)
            ),
            Vertex(
                glm.vec3(-half,  half,  half),
                glm.vec3(0,  1,  0),
                glm.vec2(0, 0)
            ),
            Vertex(
                glm.vec3(-half,  half, -half),
                glm.vec3(0,  1,  0),
                glm.vec2(0, 0)
            ),
            Vertex(
                glm.vec3(half,  half,  half),
                glm.vec3(0,  0,  1),
                glm.vec2(0, 0)
            ),
            Vertex(
                glm.vec3(-half,  half,  half),
                glm.vec3(0,  0,  1),
                glm.vec2(0, 0)
            ),
            Vertex(
                glm.vec3(half, -half,  half),
                glm.vec3(0,  0,  1),
                glm.vec2(0, 0)
            ),
            Vertex(
                glm.vec3(-half, -half,  half),
                glm.vec3(0,  0,  1),
                glm.vec2(0, 0)
            ),
            Vertex(
                glm.vec3(half, -half, -half),
                glm.vec3(0, -1,  0),
                glm.vec2(0, 0)
            ),
            Vertex(
                glm.vec3(-half, -half, -half),
                glm.vec3(0, -1,  0),
                glm.vec2(0, 0)
            ),
            Vertex(
                glm.vec3(half, -half,  half),
                glm.vec3(0, -1,  0),
                glm.vec2(0, 0)
            ),
            Vertex(
                glm.vec3(-half, -half,  half),
                glm.vec3(0, -1,  0),
                glm.vec2(0, 0)
            ),
            Vertex(
                glm.vec3(half,  half, -half),
                glm.vec3(0,  0, -1),
                glm.vec2(0, 0)
            ),
            Vertex(
                glm.vec3(-half,  half, -half),
                glm.vec3(0,  0, -1),
                glm.vec2(0, 0)
            ),
            Vertex(
                glm.vec3(half, -half, -half),
                glm.vec3(0,  0, -1),
                glm.vec2(0, 0)
            ),
            Vertex(
                glm.vec3(-half, -half, -half),
                glm.vec3(0,  0, -1),
                glm.vec2(0, 0)
            ),
            Vertex(
                glm.vec3(half,  half,  half),
                glm.vec3(1,  0,  0),
                glm.vec2(0, 0)
            ),
            Vertex(
                glm.vec3(half,  half, -half),
                glm.vec3(1,  0,  0),
                glm.vec2(0, 0)
            ),
            Vertex(
                glm.vec3(half, -half,  half),
                glm.vec3(1,  0,  0),
                glm.vec2(0, 0)
            ),
            Vertex(
                glm.vec3(half, -half, -half),
                glm.vec3(1,  0,  0),
                glm.vec2(0, 0)
            ),
            Vertex(
                glm.vec3(-half,  half,  half),
                glm.vec3(-1,  0,  0),
                glm.vec2(0, 0)
            ),
            Vertex(
                glm.vec3(-half,  half, -half),
                glm.vec3(-1,  0,  0),
                glm.vec2(0, 0)
            ),
            Vertex(
                glm.vec3(-half, -half,  half),
                glm.vec3(-1,  0,  0),
                glm.vec2(0, 0)
            ),
            Vertex(
                glm.vec3(-half, -half, -half),
                glm.vec3(-1,  0,  0),
                glm.vec2(0, 0)
            )
        ]

        cube_indices: List[int] = [
            0, 1, 2,
            1, 2, 3,
            4, 5, 6,
            5, 6, 7,
            8, 9, 10,
            9, 10, 11,
            12, 13, 14,
            14, 13, 15,
            16, 17, 18,
            17, 18, 19,
            20, 21, 22,
            22, 21, 23
        ]

        cube_mesh = Mesh(cube_vertices, cube_indices)
        cube_shader = Shader("src/shaders/polygon.vert",
                             "src/shaders/polygon.frag")
        cube_material = Material(cube_shader, glm.vec4(0.5, 0.5, 0.9, 1.0))
        cube_transform = Transform(
            glm.vec3(0.0, 0.0, 0.0),
            glm.quat(1.0, 0.0, 0.0, 0.0),
            glm.vec3(1.0, 1.0, 1.0)
        )
        cube_model = Model(
            [cube_mesh],
            [cube_material],
            [cube_transform]
        )
        self.cube_entity = Entity(cube_model, cube_transform)

    def set_transform(self, transform: Transform) -> None:
        if self.cube_entity:
            self.cube_entity.set_translation(transform.get_position())
            self.cube_entity.set_rotation(transform.get_rotation())
            self.cube_entity.set_scale(transform.get_scale())

    def render(self, renderer: Renderer, camera: Camera, light: Light) -> None:
        renderer.render_entity(camera, self.cube_entity, light)
