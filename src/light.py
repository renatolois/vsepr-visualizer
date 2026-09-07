import glm
from typing import Optional


class Light:
    def __init__(
        self,
        color: Optional[glm.vec3] = None,
        intensity: float = 1.0
    ):
        if color is None:
            color = glm.vec3(1.0, 1.0, 1.0)

        self.translation: glm.vec3 = glm.vec3(0.0, 0.0, 0.0)
        self.color: glm.vec3 = color
        self.intensity: float = intensity

    def translate(self, translation: glm.vec3) -> None:
        self.translation += translation

    def translate_xyz(self, x: float, y: float, z: float) -> None:
        self.translation += glm.vec3(x, y, z)

    def set_translation(self, translation: glm.vec3) -> None:
        self.translation = translation

    def set_translation_xyz(self, x: float, y: float, z: float) -> None:
        self.translation = glm.vec3(x, y, z)

    def set_color(self, color: glm.vec3) -> None:
        self.color = color

    def set_color_rgb(self, r: float, g: float, b: float) -> None:
        self.color = glm.vec3(r, g, b)

    def set_intensity(self, intensity: float) -> None:
        self.intensity = intensity

    def get_intensity(self) -> float:
        return self.intensity

    def get_color(self) -> glm.vec3:
        return self.color

    def get_translation(self) -> glm.vec3:
        return self.translation
