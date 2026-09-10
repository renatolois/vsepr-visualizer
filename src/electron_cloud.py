import math
import glm
from polygons.sphere import Sphere
from transform import Transform
from entity import Entity
from renderer import Renderer
from camera import Camera
from light import Light


def get_circle_vertices_xy(
    radius: float,
    num_pos: int
) -> list[glm.vec3]:
    vertices = []
    num_pos = max(num_pos, 3)
    angle = 2 * math.pi / num_pos

    current_angle = 0
    for i in range(num_pos):
        vertices.append(
            glm.vec3(
                math.cos(current_angle) * radius,
                math.sin(current_angle) * radius,
                0.0
            )
        )
        current_angle = current_angle + angle

    return vertices


class ElectronCloud:
    def __init__(
        self,
        num_electrons: int,
        radius: float,
        electron_radius: float = 0.2,
        color: glm.vec4 = glm.vec4(0.7, 0.7, 0.1, 1.0),
        speed: float = 2.0,
        decay_rate: float = 5.0,  # obsolet param
        num_positions: int = 60  # better with multiple of num_electrons
    ):
        self.num_electrons = num_electrons
        self.num_positions = num_positions
        self.positions = get_circle_vertices_xy(radius, num_positions)
        self.positions_gap = num_positions / self.num_electrons
        self.speed = speed / (2*math.pi / self.positions_gap)
        self.electrons_and_positions_indexes = []
        self.decay_rate = decay_rate
        self.color = color
        self.electron_radius = electron_radius

        electron_cloud_transform = Transform(
            glm.vec3(0.0, 0.0, 0.0),
            glm.quat(1.0, 0.0, 0.0, 0.0),
            glm.vec3(1.0, 1.0, 1.0)
        )

        self.electron_cloud_entity = Entity(model=None, transform=electron_cloud_transform)

        for i in range(num_electrons):
            index_float = self.positions_gap * i

            electron = Sphere (
                radius=self.electron_radius,
                lat_level=4,
                lon_level=4,
                sphere_color=glm.vec4(0.2, 0.6, 0.9, 1.0)
            )

            electron_transform = Transform()
            electron_transform.set_position(self.positions[ int(index_float) ])
            electron.set_transform(electron_transform)
            electron.set_color(self.color)

            self.electrons_and_positions_indexes.append((electron, index_float))
            self.electron_cloud_entity.add_child(electron.sphere_entity)

    def _get_position_from_index(self, idx: float) -> glm.vec3:
        idx = idx % self.num_positions
        i0 = int(math.floor(idx))
        i1 = (i0 + 1) % self.num_positions
        frac = idx - i0
        return glm.mix(self.positions[i0], self.positions[i1], frac)

    def update_positions(self, delta_time: float) -> None:
        for i in range(self.num_electrons):
            electron, position_index = self.electrons_and_positions_indexes[i]
            position_index += delta_time * self.speed
            position = self._get_position_from_index(position_index)
            electron.get_transform().set_position(position)
            self.electrons_and_positions_indexes[i] = (electron, position_index)

    """
    def update_positions(self, delta_time: float) -> None:
        for i in range(self.num_electrons):
            electron, position_index = self.electrons_and_positions_indexes[i]
            new_position_index = position_index + delta_time * self.speed

            smoothed_position = Transform.smooth_position (
                self.positions[ int(position_index) % self.num_positions],
                self.positions[ int(new_position_index) % self.num_positions],
                self.decay_rate,
                delta_time
            )

            electron.get_transform().set_position(smoothed_position)

            self.electrons_and_positions_indexes[i] = (electron, new_position_index % self.num_positions)
    """

    def set_speed(self, speed: float) -> None:
        self.speed = speed / (2*math.pi / self.positions_gap)

    def get_transform(self) ->  Transform:
        return self.electron_cloud_entity.get_transform()

    def set_transform(self, transform: Transform) -> None:
        self.electron_cloud_entity.set_transform(transform)

    def set_color(self, color: glm.vec4) -> None:
        for i in self.electrons_and_positions_indexes:
            electron = i[0]
            electron.set_color(color)

    def get_color(self) -> glm.vec4:
        return self.electrons_and_positions_indexes[0][0].get_color()

    def render(self, renderer: Renderer, camera: Camera, light: Light) -> None:
        renderer.render_entity(camera, self.electron_cloud_entity, light)
        
