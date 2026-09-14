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


class Cylinder:
    def __init__(
        self,
        size_factor: float,
        color: glm.vec4 = glm.vec4(0.2, 0.4, 0.6, 1.0),
        segments: int = 32
    ):
        radius = size_factor * 0.5
        half_height = size_factor * 0.5

        vertices: List[Vertex] = []
        indices: List[int] = []

        for j in range(segments + 1):
            u = j / segments
            theta = u * 2.0 * math.pi

            x = math.cos(theta)
            z = math.sin(theta)

            normal = glm.vec3(x, 0.0, z)
            pos_top = glm.vec3(x * radius, half_height, z * radius)
            pos_bottom = glm.vec3(x * radius, -half_height, z * radius)

            vertices.append(Vertex(pos_top, normal, glm.vec2(u, 1.0)))
            vertices.append(Vertex(pos_bottom, normal, glm.vec2(u, 0.0)))

        for j in range(segments):
            a = j * 2
            b = a + 1
            c = a + 2
            d = a + 3

            indices += [a, b, c]
            indices += [c, b, d]

        top_center_idx = len(vertices)
        vertices.append(Vertex(
            glm.vec3(0.0, half_height, 0.0),
            glm.vec3(0.0, 1.0, 0.0),
            glm.vec2(0.5, 0.5)
        ))

        bottom_center_idx = len(vertices)
        vertices.append(Vertex(
            glm.vec3(0.0, -half_height, 0.0),
            glm.vec3(0.0, -1.0, 0.0),
            glm.vec2(0.5, 0.5)
        ))

        top_ring_start = len(vertices)
        for j in range(segments + 1):
            u = j / segments
            theta = u * 2.0 * math.pi
            x = math.cos(theta)
            z = math.sin(theta)

            vertices.append(Vertex(
                glm.vec3(x * radius, half_height, z * radius),
                glm.vec3(0.0, 1.0, 0.0),
                glm.vec2(x * 0.5 + 0.5, z * 0.5 + 0.5)
            ))

        bottom_ring_start = len(vertices)
        for j in range(segments + 1):
            u = j / segments
            theta = u * 2.0 * math.pi
            x = math.cos(theta)
            z = math.sin(theta)

            vertices.append(Vertex(
                glm.vec3(x * radius, -half_height, z * radius),
                glm.vec3(0.0, -1.0, 0.0),
                glm.vec2(x * 0.5 + 0.5, z * 0.5 + 0.5)
            ))

        for j in range(segments):
            a = top_ring_start + j
            b = top_ring_start + j + 1
            indices += [top_center_idx, a, b]

            c = bottom_ring_start + j
            d = bottom_ring_start + j + 1
            indices += [bottom_center_idx, d, c]

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
