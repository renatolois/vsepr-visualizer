from glm import vec4
from atom import Atom
from atom_constants import HYDROGEN_SPHERE_COLOR


class Hydrogen(Atom):
    sphere_color: vec4 = HYDROGEN_SPHERE_COLOR
    radius_constant_factor: float = 0.4

    def __init__(
        self,
        tag_id: int,
        tag_size: float,
        sphere_lat_level: int = 3,
        sphere_lon_level: int = 3
    ) -> None:
        super().__init__(
            tag_id,
            tag_size,
            Hydrogen.radius_constant_factor,
            sphere_lat_level,
            sphere_lon_level,
            Hydrogen.sphere_color
        )
