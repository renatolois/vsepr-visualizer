import glfw
import OpenGL.GL as gl
import glm

from window import Window
from camera import Camera
from vision import Vision
from renderer import Renderer
from light import Light
from transform import Transform

from polygons.cone import Cone
from polygons.cube import Cube
from polygons.cuboid import Cuboid
from polygons.cylinder import Cylinder
from polygons.icosahedron import Icosahedron
from polygons.octahedron import Octahedron
from polygons.pentagonal_bipyramid import PentagonalBipyramid
from polygons.rhombic_dipyramid import RhombicDipyramid
from polygons.sphere import Sphere
from polygons.square_antiprism import SquareAntiprism
from polygons.square_pyramid import SquarePyramid
from polygons.tetrahedron import Tetrahedron
from polygons.triangular_prism import TriangularPrism
from polygons.triangular_pyramid import TriangularPyramid
from polygons.trigonal_bipyramid import TrigonalBipyramid

TAG_SIZE_METERS = 0.02
MAX_LOST_TIME_TOLERATION = 0.5


class TagState:
    def __init__(self):
        self.active = False
        self.time_since_lost = 999.0
        self.current_transform = Transform()
        self.last_transform = Transform()


def main_math(camera_id: int = 0):
    win = Window(800, 600, "Polygons Marker Visualizer")
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
        aspect=win.get_aspect_ratio()
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

    polygons_map = {
        30: Cone(TAG_SIZE_METERS, glm.vec4(0.9, 0.3, 0.6, 1.0)),
        31: Cube(TAG_SIZE_METERS, glm.vec4(0.9, 0.7, 0.6, 1.0)),
        32: Cuboid(TAG_SIZE_METERS, glm.vec4(0.3, 0.5, 0.7, 1.0)),
        33: Cylinder(TAG_SIZE_METERS, glm.vec4(0.3, 0.7, 0.9, 1.0)),
        34: Icosahedron(TAG_SIZE_METERS, glm.vec4(0.9, 0.8, 0.2, 1.0)),
        35: Octahedron(TAG_SIZE_METERS, glm.vec4(0.2, 0.9, 0.5, 1.0)),
        36: PentagonalBipyramid(TAG_SIZE_METERS, glm.vec4(0.8, 0.4, 0.9, 1.0)),
        37: RhombicDipyramid(TAG_SIZE_METERS, glm.vec4(0.5, 0.9, 0.3, 1.0)),
        38: Sphere(radius=TAG_SIZE_METERS/2, sphere_color=glm.vec4(0.9, 0.3, 0.4, 1.0), lon_level=4, lat_level=4),
        39: SquareAntiprism(TAG_SIZE_METERS, glm.vec4(0.9, 0.6, 0.2, 1.0)),
        40: SquarePyramid(TAG_SIZE_METERS, glm.vec4(0.2, 0.7, 0.5, 1.0)),
        41: Tetrahedron(TAG_SIZE_METERS, glm.vec4(0.9, 0.4, 0.2, 1.0)),
        42: TriangularPrism(TAG_SIZE_METERS, glm.vec4(0.6, 0.2, 0.9, 1.0)),
        43: TriangularPyramid(TAG_SIZE_METERS, glm.vec4(0.9, 0.9, 0.3, 1.0)),
        44: TrigonalBipyramid(TAG_SIZE_METERS, glm.vec4(0.4, 0.8, 0.9, 1.0))
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
                    TAG_SIZE_METERS
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
        for tag_id, poly in polygons_map.items():
            if not rendered_one and tag_id in detected_tags and detected_tags[tag_id].active:
                state = detected_tags[tag_id]
                
                smooth_transform = Transform.smooth_transform(
                    state.last_transform,
                    state.current_transform,
                    25.0,
                    delta_time
                )
                
                state.current_transform = smooth_transform

                poly.set_transform(smooth_transform)
                poly.render(renderer, camera, light)
                rendered_one = True

        win.swap_buffers()
        win.poll_events()

    vision.close()
    win.destroy()
    glfw.terminate()
    return 0


if __name__ == "__main__":
    main_math()