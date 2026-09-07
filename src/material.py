from shader import Shader
import glm


class Material:
    def __init__(
            self,
            shader: Shader = None,
            color: glm.vec4 = glm.vec4(0.8, 0.8, 0.8, 1.0),
            shininess: float = 32.0
    ):
        self.shader = shader
        self.color = color
        self.shininess = shininess

    def apply(self):
        self.shader.use()
        self.shader.set_uniform("material.color", self.color)
        self.shader.set_uniform("material.shininess", self.shininess)

    def set_uniform(self, *args, **kwargs):
        self.shader.set_uniform(*args, **kwargs)

    def get_color(self):
        return self.color

    def set_color(self, color: glm.vec4):
        self.color = color

    def set_color_rgba(self, r: float, g: float, b: float, a: float):
        self.color = glm.vec4(r, g, b, a)

    def set_shader(self, shader: Shader):
        self.shader = shader

    def get_shader(self):
        return self.shader

    def set_shininess(self, shininess: float):
        self.shininess = shininess

    def get_shininess(self):
        return self.shininess
