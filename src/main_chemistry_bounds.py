import glfw
import OpenGL.GL as gl
import glm

from window import Window
from camera import Camera
from vision import Vision
from renderer import Renderer
from light import Light
from transform import Transform

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

MIN_CHLORINE_DIST = 0.05
CHLORINE_RELEASE_DIST = 0.09

MIN_H2O_DIST = 0.06
H2O_RELEASE_DIST = 0.10

COLOR_CHLORINE_NORMAL = glm.vec4(0.1, 0.8, 0.3, 1.0)
COLOR_CHLORINE_BONDED = glm.vec4(0.1, 0.4, 0.9, 1.0)

COLOR_HYDROGEN_NORMAL = glm.vec4(0.9, 0.9, 0.9, 1.0)
COLOR_OXYGEN_NORMAL = glm.vec4(0.9, 0.2, 0.2, 1.0)
COLOR_H2O_BONDED = glm.vec4(0.2, 0.6, 1.0, 1.0)


class TagState:

    def __init__(self):
        self.active = False
        self.time_since_lost = 999.0
        self.current_transform = Transform()
        self.last_transform = Transform()


def main_chemistry_bounds(camera_id: int = 0):
    win = Window(800, 600, "Atoms Marker Visualizer - Bonds")
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

    vision = Vision(camera_id)
    vision.open()

    renderer = Renderer()

    hydrogen_0 = Hydrogen(radius=TAG_SIZE_METERS / 2.0)
    hydrogen_1 = Hydrogen(radius=TAG_SIZE_METERS / 2.0)
    oxygen_0 = Oxygen(radius=TAG_SIZE_METERS / 2.0)
    chlorine_0 = Chlorine(radius=TAG_SIZE_METERS / 2.0)
    chlorine_1 = Chlorine(radius=TAG_SIZE_METERS / 2.0)

    elements_map = {
        60: hydrogen_0,
        61: hydrogen_1,
        62: Carbon(radius=TAG_SIZE_METERS / 2.0),
        63: Nitrogen(radius=TAG_SIZE_METERS / 2.0),
        64: oxygen_0,
        65: Fluorine(radius=TAG_SIZE_METERS / 2.0),
        66: Neon(radius=TAG_SIZE_METERS / 2.0),
        67: chlorine_0,
        68: chlorine_1,
    }

    detected_tags = {}
    last_tag_IDs = []
    
    chlorine_bonded = False
    h2o_bonded = False

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

        if (
            67 in detected_tags and detected_tags[67].active and
            68 in detected_tags and detected_tags[68].active
        ):
            pos_c0 = detected_tags[67].current_transform.get_position()
            pos_c1 = detected_tags[68].current_transform.get_position()
            dist_cl = glm.distance(pos_c0, pos_c1)

            if not chlorine_bonded and dist_cl < MIN_CHLORINE_DIST:
                chlorine_bonded = True
            elif chlorine_bonded and dist_cl > CHLORINE_RELEASE_DIST:
                chlorine_bonded = False
        else:
            chlorine_bonded = False

        if (
            60 in detected_tags and detected_tags[60].active and
            61 in detected_tags and detected_tags[61].active and
            64 in detected_tags and detected_tags[64].active
        ):
            pos_o = detected_tags[64].current_transform.get_position()
            pos_h0 = detected_tags[60].current_transform.get_position()
            pos_h1 = detected_tags[61].current_transform.get_position()

            dist_h0_o = glm.distance(pos_h0, pos_o)
            dist_h1_o = glm.distance(pos_h1, pos_o)

            if not h2o_bonded and (dist_h0_o < MIN_H2O_DIST and dist_h1_o < MIN_H2O_DIST):
                h2o_bonded = True
            elif h2o_bonded and (dist_h0_o > H2O_RELEASE_DIST or dist_h1_o > H2O_RELEASE_DIST):
                h2o_bonded = False
        else:
            h2o_bonded = False

        target_color_cl = COLOR_CHLORINE_BONDED if chlorine_bonded else COLOR_CHLORINE_NORMAL
        chlorine_0.set_nucleus_color(Transform.smooth_color(chlorine_0.get_nucleus_color(), target_color_cl, 3.5, delta_time))
        chlorine_1.set_nucleus_color(Transform.smooth_color(chlorine_1.get_nucleus_color(), target_color_cl, 3.5, delta_time))

        target_color_h2o = COLOR_H2O_BONDED if h2o_bonded else COLOR_OXYGEN_NORMAL
        oxygen_0.set_nucleus_color(Transform.smooth_color(oxygen_0.get_nucleus_color(), target_color_h2o, 3.5, delta_time))
        
        target_color_h = COLOR_H2O_BONDED if h2o_bonded else COLOR_HYDROGEN_NORMAL
        hydrogen_0.set_nucleus_color(Transform.smooth_color(hydrogen_0.get_nucleus_color(), target_color_h, 3.5, delta_time))
        hydrogen_1.set_nucleus_color(Transform.smooth_color(hydrogen_1.get_nucleus_color(), target_color_h, 3.5, delta_time))

        bonded_transforms = {}

        if chlorine_bonded:
            p0 = detected_tags[67].current_transform.get_position()
            p1 = detected_tags[68].current_transform.get_position()
            midpoint = glm.mix(p0, p1, 0.5)
            direction = p1 - p0
            direction = glm.normalize(direction) if glm.length(direction) > 0.0001 else glm.vec3(1.0, 0.0, 0.0)
            bond_offset = direction * 0.012

            t0 = Transform(detected_tags[67].current_transform)
            t0.set_position(midpoint - bond_offset)
            bonded_transforms[67] = t0

            t1 = Transform(detected_tags[68].current_transform)
            t1.set_position(midpoint + bond_offset)
            bonded_transforms[68] = t1

        if h2o_bonded:
            pos_o = detected_tags[64].current_transform.get_position()
            
            t_ox = Transform(detected_tags[64].current_transform)
            t_ox.set_position(pos_o)
            bonded_transforms[64] = t_ox

            t_h0 = Transform(detected_tags[60].current_transform)
            t_h0.set_position(pos_o + glm.vec3(-0.015, -0.01, 0.0))
            bonded_transforms[60] = t_h0

            t_h1 = Transform(detected_tags[61].current_transform)
            t_h1.set_position(pos_o + glm.vec3(0.015, -0.01, 0.0))
            bonded_transforms[61] = t_h1

        for tag_id, element in elements_map.items():
            element.update_positions(delta_time)

            if tag_id in detected_tags and detected_tags[tag_id].active:
                state = detected_tags[tag_id]

                smooth_transform = Transform.smooth_transform(
                    state.last_transform,
                    state.current_transform,
                    25.0,
                    delta_time,
                )
                state.current_transform = smooth_transform

                if tag_id in bonded_transforms:
                    smooth_bonded = Transform.smooth_transform(
                        element.get_transform(),
                        bonded_transforms[tag_id],
                        20.0,
                        delta_time,
                    )
                    element.set_transform(smooth_bonded)
                else:
                    element.set_transform(smooth_transform)

                element.render(renderer, camera, light)

        win.swap_buffers()
        win.poll_events()

    vision.close()
    win.destroy()
    glfw.terminate()
    return 0


if __name__ == "__main__":
    main_chemistry_bounds()