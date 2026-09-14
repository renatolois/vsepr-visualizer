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


class Octahedron:
    def __init__(
        self,
        size_factor: float,
        color: glm.vec4 = glm.vec4(0.2, 0.4, 0.6, 1.0)
    ):
        h = size_factor * 0.5

        v0 = glm.vec3( h, 0, 0)
        v1 = glm.vec3(-h, 0, 0)
        v2 = glm.vec3(0,  h, 0)
        v3 = glm.vec3(0, -h, 0)
        v4 = glm.vec3(0, 0,  h)
        v5 = glm.vec3(0, 0, -h)

        def face(p0, p1, p2):
            n = glm.normalize(glm.cross(p1 - p0, p2 - p0))
            return [
                Vertex(p0, n, glm.vec2(0, 0)),
                Vertex(p1, n, glm.vec2(0, 0)),
                Vertex(p2, n, glm.vec2(0, 0)),
            ]

        vertices: List[Vertex] = []
        vertices += face(v0, v2, v4)
        vertices += face(v2, v1, v4)
        vertices += face(v1, v3, v4)
        vertices += face(v3, v0, v4)
        vertices += face(v2, v0, v5)
        vertices += face(v1, v2, v5)
        vertices += face(v3, v1, v5)
        vertices += face(v0, v3, v5)

        indices: List[int] = [
            0, 1, 2,
            3, 4, 5,
            6, 7, 8,
            9, 10, 11,
            12, 13, 14,
            15, 16, 17,
            18, 19, 20,
            21, 22, 23
        ]

        mesh = Mesh(vertices, indices)
        shader = Shader("src/shaders/polygon.vert", "src/shaders/polygon.frag")
        material = Material(shader, color)

        piece_transform = Transform(
            glm.vec3(0.0, 0.0, 0.0),
            glm.quat(1.0, 0.0, 0.0, 0.0),
            glm.vec3(1.0, 1.0, 1.0)
        )
        entity_transform = Transform(
            glm.vec3(0.0, 0.0, 0.0),
            glm.quat(1.0, 0.0, 0.0, 0.0),
            glm.vec3(1.0, 1.0, 1.0)
        )

        model = Model([mesh], [material], [piece_transform])
        self.entity = Entity(model, entity_transform)

    def set_transform(self, transform: Transform) -> None:
        if self.entity:
            self.entity.set_translation(transform.get_position())
            self.entity.set_rotation(transform.get_rotation())
            self.entity.set_scale(transform.get_scale())

    def render(self, renderer: Renderer, camera: Camera, light: Light) -> None:
        renderer.render_entity(camera, self.entity, light)
