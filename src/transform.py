import math
import glm


class Transform:
    def __init__(
            self,
            position: glm.vec3 = None,
            rotation: glm.quat = None,
            scale: glm.vec3 = None
    ):
        self.position = (
            position if position is not None
            else glm.vec3(1.0, 1.0, 1.0)
        )

        self.rotation = (
            rotation if rotation is not None
            else glm.quat(1.0, 0.0, 0.0, 0.0)
        )

        self.scale = (
            scale if scale is not None
            else glm.vec3(1.0, 1.0, 1.0)
        )

        self.cached_model_matrix = glm.mat4(1.0)
        self.dirty = True

    @staticmethod
    def smooth_transform(
            current_transform: 'Transform',
            target: 'Transform',
            decay_rate: float,
            delta_time: float
    ) -> 'Transform':
        alpha = 1.0 - math.exp(-decay_rate * delta_time)

        smoothed_position = glm.mix(
            current_transform.get_position(),
            target.get_position(),
            alpha
        )

        q_target = target.get_rotation()
        q_current = current_transform.get_rotation()

        if glm.dot(q_current, q_target) < 0.0:
            q_target = -q_target

        smoothed_rotation = glm.slerp(
            current_transform.get_rotation(),
            q_target,
            alpha
        )

        smoothed_scale = glm.mix(
            current_transform.get_scale(),
            target.get_scale(),
            alpha
        )

        return Transform(smoothed_position, smoothed_rotation, smoothed_scale)

    @staticmethod
    def smooth_color(
            current_color: glm.vec4,
            target_color: glm.vec4,
            speed: float,
            delta_time: float
    ) -> glm.vec4:
        factor = max(0.0, min(speed * delta_time, 1.0))
        return glm.mix(current_color, target_color, factor)

    @staticmethod
    def smooth_color_exponential(
            current_color: glm.vec4,
            target_color: glm.vec4,
            decay_rate: float,
            delta_time: float
    ) -> glm.vec4:
        alpha = 1.0 - math.exp(-decay_rate * delta_time)
        return glm.mix(current_color, target_color, alpha)

    def set_position(self, position: glm.vec3):
        self.position = position
        self.dirty = True

    def set_rotation(self, rotation: glm.quat):
        self.rotation = rotation
        self.dirty = True

    def set_scale(self, scale: glm.vec3):
        self.scale = scale
        self.dirty = True

    def get_position(self) -> glm.vec3:
        return self.position

    def get_rotation(self) -> glm.quat:
        return self.rotation

    def get_scale(self) -> glm.vec3:
        return self.scale

    def get_model_matrix(self) -> glm.mat4:
        if self.dirty:
            self.cached_model_matrix = glm.mat4(1.0)
            self.cached_model_matrix = (
                    glm.translate(self.cached_model_matrix, self.position)
            )

            self.cached_model_matrix = (
                    self.cached_model_matrix * glm.mat4_cast(self.rotation)
            )

            self.cached_model_matrix = (
                    glm.scale(self.cached_model_matrix, self.scale)
            )

            self.dirty = False

        return self.cached_model_matrix

    def translate_local(self, offset: glm.vec3):
        self.position += self.rotation * offset
        self.dirty = True

    def translate_global(self, offset: glm.vec3):
        self.position += offset
        self.dirty = True
