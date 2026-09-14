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


class Cone:
    def __init__(
        self,
        size_factor: float,
        color: glm.vec4 = glm.vec4(0.2, 0.4, 0.6, 1.0),
        segments: int = 64
    ):
        radius = size_factor * 0.5
        half_height = size_factor * 0.5

        apex = glm.vec3(0.0, half_height, 0.0)

        vertices: List[Vertex] = []
        indices: List[int] = []

        for j in range(segments):
            theta0 = (j / segments) * 2.0 * math.pi
            theta1 = ((j + 1) / segments) * 2.0 * math.pi

            x0 = math.cos(theta0)
            z0 = math.sin(theta0)
            x1 = math.cos(theta1)
            z1 = math.sin(theta1)

            p0 = glm.vec3(x0 * radius, -half_height, z0 * radius)
            p1 = glm.vec3(x1 * radius, -half_height, z1 * radius)

            e0 = p0 - apex
            e1 = p1 - apex
            n = glm.normalize(glm.cross(e1, e0))

            base = len(vertices)
            vertices.append(Vertex(apex, n, glm.vec2(0.5, 1.0)))
            vertices.append(Vertex(p0, n, glm.vec2(0.0, 0.0)))
            vertices.append(Vertex(p1, n, glm.vec2(1.0, 0.0)))

            indices += [base + 0, base + 1, base + 2]

        base_center_idx = len(vertices)
        vertices.append(Vertex(
            glm.vec3(0.0, -half_height, 0.0),
            glm.vec3(0.0, -1.0, 0.0),
            glm.vec2(0.5, 0.5)
        ))

        base_ring_start = len(vertices)
        for j in range(segments + 1):
            theta = (j / segments) * 2.0 * math.pi
            x = math.cos(theta)
            z = math.sin(theta)

            vertices.append(Vertex(
                glm.vec3(x * radius, -half_height, z * radius),
                glm.vec3(0.0, -1.0, 0.0),
                glm.vec2(x * 0.5 + 0.5, z * 0.5 + 0.5)
            ))

        for j in range(segments):
            a = base_ring_start + j
            b = base_ring_start + j + 1
            indices += [base_center_idx, b, a]

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
