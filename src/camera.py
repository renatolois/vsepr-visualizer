import glm
import math
from typing import Optional


class Camera:
    def __init__(
        self,
        position: Optional[glm.vec3] = None,
        world_up: Optional[glm.vec3] = None,
        yaw: float = -90.0,
        pitch: float = 0.0,
        aspect: float = 4.0 / 3.0
    ):
        if position is None:
            position = glm.vec3(0.0, 0.0, 0.0)
        if world_up is None:
            world_up = glm.vec3(0.0, 1.0, 0.0)

        self.position: glm.vec3 = position
        self.world_up: glm.vec3 = world_up
        self.yaw: float = yaw
        self.pitch: float = pitch
        self.aspect: float = aspect

        self.front: glm.vec3 = glm.vec3(0.0, 0.0, -1.0)
        self.right: glm.vec3 = glm.vec3(0.0, 0.0, 0.0)
        self.up: glm.vec3 = glm.vec3(0.0, 0.0, 0.0)

        self.zoom: float = 45.0
        self.near: float = 0.01
        self.far: float = 100.0

        self.cached_view_matrix: glm.mat4 = glm.mat4(1.0)
        self.cached_projection_matrix: glm.mat4 = glm.mat4(1.0)
        self.dirty_view: bool = True
        self.dirty_projection: bool = True

        self.update_camera_vectors()

    @classmethod
    def from_scalars(
        cls,
        pos_x: float,
        pos_y: float,
        pos_z: float,
        world_up_x: float,
        world_up_y: float,
        world_up_z: float,
        yaw: float,
        pitch: float,
        aspect: float = 4.0 / 3.0
    ) -> 'Camera':
        position = glm.vec3(pos_x, pos_y, pos_z)
        world_up = glm.vec3(world_up_x, world_up_y, world_up_z)
        return cls(position, world_up, yaw, pitch, aspect)

    def update_camera_vectors(self) -> None:
        new_front: glm.vec3 = glm.vec3(
            math.cos(glm.radians(self.yaw))*math.cos(glm.radians(self.pitch)),
            math.sin(glm.radians(self.pitch)),
            math.sin(glm.radians(self.yaw))*math.cos(glm.radians(self.pitch))
        )

        self.front = glm.normalize(new_front)
        self.right = glm.normalize(glm.cross(self.front, self.world_up))
        self.up = glm.normalize(glm.cross(self.right, self.front))

        self.dirty_view = True

    def get_aspect(self) -> float:
        return self.aspect

    def get_zoom(self) -> float:
        return self.zoom

    def get_near(self) -> float:
        return self.near

    def get_far(self) -> float:
        return self.far

    def get_yaw(self) -> float:
        return self.yaw

    def get_pitch(self) -> float:
        return self.pitch

    def get_position(self) -> glm.vec3:
        return self.position

    def get_view_matrix(self) -> glm.mat4:
        if not self.dirty_view:
            return self.cached_view_matrix

        self.cached_view_matrix = glm.lookAt(
            self.position,
            self.position + self.front,
            self.up
        )

        self.dirty_view = False
        return self.cached_view_matrix

    def get_projection_matrix(self) -> glm.mat4:
        if not self.dirty_projection:
            return self.cached_projection_matrix

        self.cached_projection_matrix = glm.perspective(
            glm.radians(self.zoom),
            self.aspect,
            self.near,
            self.far
        )

        self.dirty_projection = False
        return self.cached_projection_matrix

    def get_ortho_matrix(self) -> glm.mat4:
        half_width: float = 1.0
        half_height: float = half_width / self.aspect
        return glm.ortho(-half_width, half_width, -half_height, half_height)

    def set_position(self, pos: glm.vec3) -> None:
        self.position = pos
        self.dirty_view = True

    def set_aspect(self, aspect: float) -> None:
        self.aspect = aspect
        self.dirty_projection = True

    def set_aspect_from_height_width(
            self,
            height: float,
            width: float
    ) -> None:
        if height == 0.0:
            print("Warning: Height cannot be 0, using default aspect 1.0")
            self.aspect = 1.0
        else:
            self.aspect = width / height
        self.dirty_projection = True

    def set_zoom(self, zoom: float) -> None:
        self.zoom = zoom
        self.dirty_projection = True

    def set_pitch(self, pitch: float) -> None:
        self.pitch = pitch
        self.update_camera_vectors()

    def set_yaw(self, yaw: float) -> None:
        self.yaw = yaw
        self.update_camera_vectors()

    def set_orientation(self, yaw: float, pitch: float) -> None:
        self.yaw = yaw
        self.pitch = pitch
        self.update_camera_vectors()

    def set_target(self, target: glm.vec3) -> None:
        direction: glm.vec3 = glm.normalize(target - self.position)
        self.pitch = glm.degrees(math.asin(direction.y))
        self.yaw = glm.degrees(math.atan2(direction.z, direction.x))
        self.update_camera_vectors()

    def set_world_up(self, up: glm.vec3) -> None:
        self.world_up = up
        self.update_camera_vectors()

    def set_near(self, near: float) -> None:
        self.near = near
        self.dirty_projection = True

    def set_far(self, far: float) -> None:
        self.far = far
        self.dirty_projection = True

    def get_front(self) -> glm.vec3:
        return self.front

    def get_right(self) -> glm.vec3:
        return self.right

    def get_up(self) -> glm.vec3:
        return self.up

    def get_world_up(self) -> glm.vec3:
        return self.world_up
