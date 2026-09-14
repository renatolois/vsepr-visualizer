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


class Icosahedron:
    def __init__(
        self,
        size_factor: float,
        color: glm.vec4 = glm.vec4(0.2, 0.4, 0.6, 1.0)
    ):
        phi = (1.0 + math.sqrt(5.0)) / 2.0

        raw = [
            glm.vec3(0,  1,  phi),
            glm.vec3(0,  1, -phi),
            glm.vec3(0, -1,  phi),
            glm.vec3(0, -1, -phi),
            glm.vec3( 1,  phi, 0),
            glm.vec3( 1, -phi, 0),
            glm.vec3(-1,  phi, 0),
            glm.vec3(-1, -phi, 0),
            glm.vec3( phi, 0,  1),
            glm.vec3( phi, 0, -1),
            glm.vec3(-phi, 0,  1),
            glm.vec3(-phi, 0, -1),
        ]

        max_len = max(math.sqrt(v.x ** 2 + v.y ** 2 + v.z ** 2) for v in raw)
        scale = (size_factor * 0.5) / max_len
        verts = [v * scale for v in raw]

        faces = [
            (0, 2, 8),
            (0, 8, 4),
            (0, 4, 6),
            (0, 6, 10),
            (0, 10, 2),
            (3, 1, 9),
            (3, 9, 5),
            (3, 5, 7),
            (3, 7, 11),
            (3, 11, 1),
            (2, 5, 8),
            (8, 5, 9),
            (8, 9, 4),
            (4, 9, 1),
            (4, 1, 6),
            (6, 1, 11),
            (6, 11, 10),
            (10, 11, 7),
            (10, 7, 2),
            (2, 7, 5),
        ]

        vertices: List[Vertex] = []
        indices: List[int] = []

        for f in faces:
            p0, p1, p2 = (verts[i] for i in f)
            n = glm.normalize(glm.cross(p1 - p0, p2 - p0))
            center = (p0 + p1 + p2) / 3.0
            if glm.dot(n, center) < 0.0:
                n = -n

            base = len(vertices)
            vertices.append(Vertex(p0, n, glm.vec2(0, 0)))
            vertices.append(Vertex(p1, n, glm.vec2(0, 0)))
            vertices.append(Vertex(p2, n, glm.vec2(0, 0)))

            indices += [base + 0, base + 1, base + 2]

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
