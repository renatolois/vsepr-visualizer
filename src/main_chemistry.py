import glfw
import OpenGL.GL as gl
import glm

from window import Window
from camera import Camera
from vision import Vision
from renderer import Renderer
from light import Light
from transform import Transform

# Importando os elementos químicos do módulo de elements (incluindo Enxofre e Cloro)
from elements import (
    Hydrogen,
    Helium,
    Carbon,
    Nitrogen,
    Oxygen,
    Fluorine,
    Neon,
    Sulfur,
    Chlorine,
)

TAG_SIZE_METERS = 0.02
MAX_LOST_TIME_TOLERATION = 0.5


class TagState:

    def __init__(self):
        self.active = False
        self.time_since_lost = 999.0
        self.current_transform = Transform()
        self.last_transform = Transform()


def main_chemistry():
    win = Window(800, 600, "Atoms Marker Visualizer")
    if win.init_backend() != 0 or win.init() != 0:
        return 1
    win.set_visible(True)
    gl.glEnable(gl.GL_DEPTH_TEST)
    gl.glClearColor(0.0, 0.0, 0.0, 1.0)

    camera = Camera(
        position=glm.vec3(0.0, 0.0, 0.0),
        world_up=glm.vec3(0.0, 1.0, 0.0),
        yaw=-90.0,
        pitch=0.0,
        aspect=win.get_aspect_ratio(),
    )
    camera.set_position(glm.vec3(0.0, 0.0, 0.0))
    camera.set_aspect(640.0 / 480.0)
    camera.set_zoom(60.0)
    camera.set_near(0.001)
    camera.set_far(10.0)

    light = Light(glm.vec3(1.0, 1.0, 1.0), 1.5)
    light.set_translation(glm.vec3(2.0, 3.0, 4.0))

    vision = Vision(camera_id=0)
    vision.open()

    renderer = Renderer()

    # Mapeamento de IDs de tags para os respectivos Elementos Químicos (60 a 68)
    elements_map = {
        60: Hydrogen(radius=TAG_SIZE_METERS / 2.0),
        61: Helium(radius=TAG_SIZE_METERS / 2.0),
        62: Carbon(radius=TAG_SIZE_METERS / 2.0),
        63: Nitrogen(radius=TAG_SIZE_METERS / 2.0),
        64: Oxygen(radius=TAG_SIZE_METERS / 2.0),
        65: Fluorine(radius=TAG_SIZE_METERS / 2.0),
        66: Neon(radius=TAG_SIZE_METERS / 2.0),
        67: Sulfur(radius=TAG_SIZE_METERS / 2.0),
        68: Chlorine(radius=TAG_SIZE_METERS / 2.0),
    }

    detected_tags = {}
    last_tag_IDs = []

    while not win.should_close():
        delta_time = 0.016
        if hasattr(win, "get_delta_time"):
            delta_time = win.get_delta_time()

        gl.glClear(gl.GL_DEPTH_BUFFER_BIT | gl.GL_COLOR_BUFFER_BIT)

        gl.glDisable(gl.GL_DEPTH_TEST)
        vision.update_camera_background(win.get_aspect_ratio())
        gl.glEnable(gl.GL_DEPTH_TEST)

        frame = vision.get_framebuffer()
        current_detected_IDs = []

        if frame is not None:
            vision.detect_markers()
            current_detected_IDs = vision.tag_IDs

            for i, tag_id in enumerate(current_detected_IDs):
                if tag_id not in detected_tags:
                    detected_tags[tag_id] = TagState()

                state = detected_tags[tag_id]
                state.last_transform = state.current_transform

                new_transform = vision.get_marker_transform(
                    vision.tags_corners[i],
                    camera,
                    float(frame.shape[1]),
                    float(frame.shape[0]),
                    TAG_SIZE_METERS,
                )

                new_transform.translate_local(glm.vec3(0.0, 0.0, TAG_SIZE_METERS))

                state.current_transform = new_transform
                state.active = True
                state.time_since_lost = 0.0

        for tag_id, state in detected_tags.items():
            if tag_id not in current_detected_IDs:
                if state.active:
                    state.time_since_lost += delta_time
                    if state.time_since_lost > MAX_LOST_TIME_TOLERATION:
                        state.active = False

        last_tag_IDs = current_detected_IDs

        rendered_one = False
        for tag_id, element in elements_map.items():
            # Atualiza a posição dos elétrons a cada frame
            element.update_positions(delta_time)

            if (
                not rendered_one
                and tag_id in detected_tags
                and detected_tags[tag_id].active
            ):
                state = detected_tags[tag_id]

                smooth_transform = Transform.smooth_transform(
                    state.last_transform,
                    state.current_transform,
                    25.0,
                    delta_time,
                )

                state.current_transform = smooth_transform

                element.set_transform(smooth_transform)
                element.render(renderer, camera, light)
                rendered_one = True

        win.swap_buffers()
        win.poll_events()

    vision.close()
    win.destroy()
    glfw.terminate()
    return 0


if __name__ == "__main__":
    main_chemistry()