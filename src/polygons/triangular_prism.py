import glm
import math
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


class TriangularPrism:
    def __init__(
        self,
        size_factor: float,
        color: glm.vec4 = glm.vec4(0.2, 0.4, 0.6, 1.0)
    ):
        h = size_factor * 0.5
        r = size_factor * 0.4

        top = [glm.vec3(math.cos(i * 2 * math.pi / 3) * r, h, math.sin(i * 2 * math.pi / 3) * r) for i in range(3)]
        bot = [glm.vec3(math.cos(i * 2 * math.pi / 3) * r, -h, math.sin(i * 2 * math.pi / 3) * r) for i in range(3)]

        def face(p0, p1, p2):
            center = (p0 + p1 + p2) / 3.0
            n = glm.normalize(glm.cross(p1 - p0, p2 - p0))
            if glm.dot(n, center) < 0:
                n = -n
                return [
                    Vertex(p0, n, glm.vec2(0)),
                    Vertex(p2, n, glm.vec2(0)),
                    Vertex(p1, n, glm.vec2(0))
                ]
            return [
                Vertex(p0, n, glm.vec2(0)),
                Vertex(p1, n, glm.vec2(0)),
                Vertex(p2, n, glm.vec2(0))
            ]

        vertices: List[Vertex] = []
        for i in range(3):
            next_i = (i + 1) % 3
            vertices += face(bot[i], bot[next_i], top[i])
            vertices += face(top[i], bot[next_i], top[next_i])

        vertices += face(bot[0], bot[2], bot[1])
        vertices += face(top[0], top[1], top[2])

        indices = list(range(len(vertices)))
        mesh = Mesh(vertices, indices)
        shader = Shader("src/shaders/polygon.vert", "src/shaders/polygon.frag")
        material = Material(shader, color)

        piece_transform = Transform(glm.vec3(0), glm.quat(1, 0, 0, 0), glm.vec3(1))
        entity_transform = Transform(glm.vec3(0), glm.quat(1, 0, 0, 0), glm.vec3(1))
        model = Model([mesh], [material], [piece_transform])
        self.entity = Entity(model, entity_transform)

    def set_transform(self, transform: Transform) -> None:
        if self.entity:
            self.entity.set_translation(transform.get_position())
            self.entity.set_rotation(transform.get_rotation())
            self.entity.set_scale(transform.get_scale())

    def render(self, renderer: Renderer, camera: Camera, light: Light) -> None:
        renderer.render_entity(camera, self.entity, light)