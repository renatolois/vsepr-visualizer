import glm
from polygons.sphere import Sphere
from electron_cloud import ElectronCloud
from light import Light
from camera import Camera
from renderer import Renderer
from transform import Transform


class Atom:
    def __init__(
        self,
        nucleus_radius: float = 0.7,
        nucleus_color: glm.vec4 = glm.vec4(1.0, 0.0, 0.0, 1.0),
        nucleus_level: int = 4,
        electron_radius: float = 0.2,
        electron_level: int = 2,
        electron_cloud_color: glm.vec4 = glm.vec4(6.0, 7.0, 0.0, 1.0),  # > 1.0 intentionally
        electron_cloud_radius: float = 3,
        electron_cloud_num_positions: int = 60,
        electron_cloud_speed: float = 2.0,
        electron_cloud_num_electrons: float = 4,
        decay_rate: float = 5.0  # obsolet param
    ) -> None:
        self.nucleus_radius = nucleus_radius
        self.nucleus_color = nucleus_color
        self.nucleus_level = nucleus_level
        self.electron_radius = electron_radius
        self.electron_level = electron_level
        self.electron_cloud_color = electron_cloud_color
        self.electron_cloud_num_electrons = electron_cloud_num_electrons
        self.electron_cloud_num_positions = electron_cloud_num_positions
        self.electron_cloud_speed = electron_cloud_speed
        self.decay_rate = decay_rate
        self.electron_cloud_radius = electron_cloud_radius

        self.atom = Sphere (
            radius=self.nucleus_radius,
            lat_level=self.nucleus_level,
            lon_level=self.nucleus_level,
            sphere_color=self.nucleus_color
        )

        self.electron_cloud = ElectronCloud (
            num_electrons=self.electron_cloud_num_electrons,
            radius=self.electron_cloud_radius,
            electron_radius=self.electron_radius,
            color=self.electron_cloud_color,
            speed=self.electron_cloud_speed,
            num_positions=self.electron_cloud_num_positions,
            decay_rate=self.decay_rate
        )

        self.atom.sphere_entity.add_child (
            self.electron_cloud.electron_cloud_entity
        )

    def set_nucleus_color(self, color: glm.vec4) -> None:
        self.atom.set_color(color)

    def get_nucleus_color(self) -> glm.vec4:
        return self.atom.get_color()

    def set_electrons_color(self, color: glm.vec4) -> None:
        self.electron_cloud.set_color(color)

    def get_electrons_color(self) -> glm.vec4:
        return self.electron_cloud.get_color()

    def get_transform(self) -> Transform:
        return self.atom.sphere_entity.get_transform()

    def set_transform(self, transform: Transform) -> None:
        self.atom.sphere_entity.set_transform(transform)

    def update_positions(self, delta_time: float) -> None:
        self.electron_cloud.update_positions(delta_time)

    def render(self, renderer: Renderer, camera: Camera, light: Light) -> None:
        renderer.render_entity(camera, self.atom.sphere_entity, light)
