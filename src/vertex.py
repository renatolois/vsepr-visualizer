import glm


class Vertex:
    def __init__(
            self,
            position: glm.vec3,
            normal: glm.vec3,
            tex_coords: glm.vec2
    ):
        self.position = position
        self.normal = normal
        self.tex_coords = tex_coords
