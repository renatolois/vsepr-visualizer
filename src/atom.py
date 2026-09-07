from glm import vec4
from polygons.sphere import Sphere


class Atom:
    def __init__(
        self,
        tag_id: int,
        tag_size: float,
        radius_constant_factor: float = 0.7,
        sphere_lat_level: int = 3,
        sphere_lon_level: int = 3,
        sphere_color: vec4 = vec4(1.0, 0.0, 0.0, 1.0)
    ) -> None:
        self.tag_id: int = tag_id
        self.tag_size: float = tag_size
        self.radius_constant_factor: float = radius_constant_factor

        self.atom_sphere: Sphere = Sphere(
            tag_size * radius_constant_factor,
            sphere_lat_level,
            sphere_lon_level,
            sphere_color
        )

    def get_tag_size(self) -> float:
        return self.tag_size

    def set_tag_id(self, tag_id: int) -> None:
        self.tag_id = tag_id

    def get_tag_id(self) -> int:
        return self.tag_id

    def get_color(self) -> vec4:
        return self.atom_sphere.get_color()

    def set_color(self, color: vec4) -> None:
        self.atom_sphere.set_color(color)
