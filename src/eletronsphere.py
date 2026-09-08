import math
import glm
from polygons.sphere import Sphere


def get_circle_vertices_xy(
    radius: float,
    num_pos: int
) -> list[float]:
    vertices = []
    num_pos = 3 if num_pos < 3 else num_pos
    angle = 2 * math.pi / num_pos

    current_angle = 0
    for i in range(num_pos):
        vertices.push[(
            math.cos(current_angle) * radius,
            math.sin(current_angle) * radius
        )]
        current_angle = current_angle + angle




class eletronsphere:
    def __init__(
        num_eletrons: int
        eletrons_speed: float,
        color: glm.vec3
    ):
        self.num_eletrons = num_eletrons
        self.eletrons_speed = eletrons_speed

        eletrons = []
        for i in range(num_eletrons)?
            elentron = Sphere (

            )

            eletrons.append(eletron)
