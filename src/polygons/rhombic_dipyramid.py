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


class RhombicDipyramid:
    def __init__(
        self,
        size_factor: float,
        color: glm.vec4 = glm.vec4(0.2, 0.4, 0.6, 1.0)
    ):
        h = size_factor * 0.6
        w = size_factor * 0.4
        
        v_top = glm.vec3(0.0, h, 0.0)
        v_bot = glm.vec3(0.0, -h, 0.0)
        v1 = glm.vec3(w, 0.0, 0.0)
        v2 = glm.vec3(0.0, 0.0, w)
        v3 = glm.vec3(-w, 0.0, 0.0)
        v4 = glm.vec3(0.0, 0.0, -w)

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

        vertices: List[Vertex] = (
            face(v1, v2, v_top) + face(v2, v3, v_top) + face(v3, v4, v_top) + face(v4, v1, v_top) +
            face(v2, v1, v_bot) + face(v3, v2, v_bot) + face(v4, v3, v_bot) + face(v1, v4, v_bot)
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