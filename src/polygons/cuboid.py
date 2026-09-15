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


class Cuboid:
    def __init__(
        self,
        size_factor: float,
        color: glm.vec4 = glm.vec4(0.2, 0.4, 0.6, 1.0)
    ):
        hx = size_factor * 0.6
        hy = size_factor * 0.4
        hz = size_factor * 0.5

        v0 = glm.vec3(hx, hy, hz)
        v1 = glm.vec3(hx, hy, -hz)
        v2 = glm.vec3(-hx, hy, hz)
        v3 = glm.vec3(-hx, hy, -hz)
        v4 = glm.vec3(hx, -hy, hz)
        v5 = glm.vec3(hx, -hy, -hz)
        v6 = glm.vec3(-hx, -hy, hz)
        v7 = glm.vec3(-hx, -hy, -hz)

        def face(p0, p1, p2):
            n = glm.normalize(glm.cross(p1 - p0, p2 - p0))
            return [Vertex(p0, n, glm.vec2(0)), Vertex(p1, n, glm.vec2(0)), Vertex(p2, n, glm.vec2(0))]

        vertices: List[Vertex] = (
            face(v2, v0, v1) + face(v2, v1, v3) +
            face(v4, v6, v7) + face(v4, v7, v5) +
            face(v6, v2, v3) + face(v6, v3, v7) +
            face(v0, v4, v5) + face(v0, v5, v1) +
            face(v2, v6, v4) + face(v2, v4, v0) +
            face(v1, v5, v7) + face(v1, v7, v3)
        )

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