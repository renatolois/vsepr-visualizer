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


class Tetrahedron:
    def __init__(
        self,
        size_factor: float,
        color: glm.vec4 = glm.vec4(0.2, 0.4, 0.6, 1.0)
    ):
        s = size_factor

        a = s * 0.5
        h = s * (2.0 ** 0.5) * 0.5
        y = h / 3.0

        v0 = glm.vec3( a, -y,  a)
        v1 = glm.vec3(-a, -y,  a)
        v2 = glm.vec3( 0, -y, -a * 2.0 ** 0.5 * 0.5 + a * 0.5)
        v3 = glm.vec3( 0,  h - y, 0)

        def face(p0, p1, p2, normal):
            return [
                Vertex(p0, normal, glm.vec2(0, 0)),
                Vertex(p1, normal, glm.vec2(0, 0)),
                Vertex(p2, normal, glm.vec2(0, 0)),
            ]

        def normal(p0, p1, p2):
            return glm.normalize(glm.cross(p2 - p0, p1 - p0))

        n0 = normal(v0, v1, v3)
        n1 = normal(v1, v2, v3)
        n2 = normal(v2, v0, v3)
        n3 = normal(v1, v0, v2)

        vertices: List[Vertex] = []
        vertices += face(v0, v1, v3, n0)
        vertices += face(v1, v2, v3, n1)
        vertices += face(v2, v0, v3, n2)
        vertices += face(v1, v0, v2, n3)

        indices: List[int] = [
            0, 1, 2,
            3, 4, 5,
            6, 7, 8,
            9, 10, 11
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
