import glfw
import OpenGL.GL as gl
import glm
import math

from window import Window
from model import Model, ModelPiece
from vertex import Vertex
from polygons.sphere import Sphere
from polygons.cube import Cube
from polygons.tetrahedron import Tetrahedron
from polygons.octahedron import Octahedron
from polygons.icosahedron import Icosahedron
from polygons.cylinder import Cylinder
from polygons.cone import Cone
from camera import Camera
from entity import Entity
from mesh import Mesh
from shader import Shader
from material import Material
from transform import Transform
from renderer import Renderer
from light import Light
from electron_cloud import ElectronCloud
from atom import Atom


def update(win, camera, camera_speed, delta_time):
    window = win.get_window()
    speed = camera_speed * delta_time
    move_dir = glm.vec3(0.0)

    front = camera.get_front()
    right = camera.get_right()
    world_up = camera.get_world_up()

    if (
        glfw.get_key(window, glfw.KEY_W) == glfw.PRESS or
        glfw.get_key(window, glfw.KEY_UP) == glfw.PRESS
    ):
        move_dir += front
    if (
        glfw.get_key(window, glfw.KEY_S) == glfw.PRESS or
        glfw.get_key(window, glfw.KEY_DOWN) == glfw.PRESS
    ):
        move_dir -= front

    if (
        glfw.get_key(window, glfw.KEY_A) == glfw.PRESS or
        glfw.get_key(window, glfw.KEY_LEFT) == glfw.PRESS
    ):
        move_dir -= right
    if (
        glfw.get_key(window, glfw.KEY_D) == glfw.PRESS or
        glfw.get_key(window, glfw.KEY_RIGHT) == glfw.PRESS
    ):
        move_dir += right

    if glfw.get_key(window, glfw.KEY_Q) == glfw.PRESS:
        move_dir += world_up

    if glfw.get_key(window, glfw.KEY_E) == glfw.PRESS:
        move_dir -= world_up

    if glm.length(move_dir) > 0.0:
        current_pos = camera.get_position()
        camera.set_position(current_pos + move_dir * speed)


def main():
    win = Window(800, 600, "VESPR - Visualizer")
    if win.init_backend() != 0 or win.init() != 0:
        return 1
    win.set_visible(True)
    gl.glEnable(gl.GL_DEPTH_TEST)
    gl.glClearColor(0.0, 0.0, 0.0, 1.0)

    camera = Camera(
        position=glm.vec3(0.0, 2.0, 10.0),
        world_up=glm.vec3(0.0, 1.0, 0.0),
        yaw=-90.0,
        pitch=0.0,
        aspect=win.get_aspect_ratio()
    )

    light = Light(glm.vec3(1.0, 1.0, 1.0), 1.5)
    light.set_translation(glm.vec3(2.0, 3.0, 4.0))

    hydrogen = Atom(
        nucleus_radius=0.5,
        nucleus_color=glm.vec4(1.00, 1.00, 1.00, 1.0),
        electron_cloud_num_electrons=1,
        electron_cloud_speed=16,
        electron_cloud_color=glm.vec4(0.9, 0.9, 0.9, 1.0),
    )
    hydrogen_transform = Transform()
    hydrogen_transform.set_position(glm.vec3(16.0, 5.0, 9.0))
    hydrogen_transform.set_rotation(
        glm.angleAxis(
            math.pi / 4,
            glm.vec3(1.0, 0.0, 0.0)
        )
    )
    hydrogen.set_transform(hydrogen_transform)

    helium = Atom(
        nucleus_radius=0.6,
        nucleus_color=glm.vec4(0.85, 1.00, 1.00, 1.0),
        electron_cloud_num_electrons=2,
        electron_cloud_speed=16,
        electron_cloud_color=glm.vec4(0.9, 0.9, 0.9, -1.0),
    )
    helium_transform = Transform()
    helium_transform.set_position(glm.vec3(7.0, 3.0, -5.0))
    helium_transform.set_rotation(
        glm.angleAxis(
            math.pi / 5,
            glm.vec3(1.0, 0.0, 0.0)
        )
    )
    helium.set_transform(helium_transform)

    carbon = Atom(
        nucleus_radius=0.7,
        nucleus_color=glm.vec4(0.30, 0.30, 0.30, 1.0),
        electron_cloud_num_electrons=4,
        electron_cloud_speed=16,
        electron_cloud_color=glm.vec4(0.9, 0.9, 0.9, -3.0),
    )
    carbon_transform = Transform()
    carbon_transform.set_position(glm.vec3(13.0, 6.0, 5.0))
    carbon.set_transform(carbon_transform)

    nitrogen = Atom(
        nucleus_radius=0.7,
        nucleus_color=glm.vec4(0.10, 0.10, 0.90, 1.0),
        electron_cloud_num_electrons=5,
        electron_cloud_speed=16,
        electron_cloud_color=glm.vec4(0.9, 0.9, 0.9, -6.0),
    )
    nitrogen_transform = Transform()
    nitrogen_transform.set_position(glm.vec3(17.0, 4.0, 11.0))
    nitrogen.set_transform(nitrogen_transform)

    oxygen = Atom(
        nucleus_radius=0.7,
        nucleus_color=glm.vec4(0.95, 0.10, 0.10, 1.0),
        electron_cloud_num_electrons=6,
        electron_cloud_speed=16,
        electron_cloud_color=glm.vec4(0.9, 0.9, 0.9, -9.0),
    )
    oxygen_transform = Transform()
    oxygen_transform.set_position(glm.vec3(11, 5.0, -5.0))
    oxygen_transform.set_rotation(
        glm.angleAxis(
            math.pi / 3,
            glm.vec3(1.0, 1.0, 0.0)
        )
    )
    oxygen.set_transform(oxygen_transform)

    fluorine = Atom(
        nucleus_radius=0.7,
        nucleus_color=glm.vec4(0.50, 1.00, 0.50, 1.0),
        electron_cloud_num_electrons=7,
        electron_cloud_speed=16,
        electron_cloud_color=glm.vec4(0.9, 0.9, 0.9, 1.0),
    )
    fluorine_transform = Transform()
    fluorine_transform.set_position(glm.vec3(-5.0, 4.0, 5.0))
    fluorine.set_transform(fluorine_transform)

    neon = Atom(
        nucleus_radius=0.7,
        nucleus_color=glm.vec4(0.85, 1.00, 1.00, 1.0),
        electron_cloud_num_electrons=8,
        electron_cloud_speed=16,
        electron_cloud_color=glm.vec4(0.9, 0.9, 0.9, 1.0),
    )
    neon_transform = Transform()
    neon_transform.set_position(glm.vec3(-21.0, 6.0, 10.0))
    neon.set_transform(neon_transform)

    electron_cloud = ElectronCloud(
        num_electrons=8,
        radius=5,
        electron_radius=1.5,
        color=glm.vec4(0.9, 0.7, 0.0, 1.0)
    )
    electron_cloud_transform = Transform()
    electron_cloud_transform.set_position(glm.vec3(-10, 10, 10))
    electron_cloud.set_transform(electron_cloud_transform)

    tetrahedron = Tetrahedron(
        size_factor=2.5,
        color=glm.vec4(0.9, 0.4, 0.2, 1.0)
    )
    tetrahedron_transform = Transform()
    tetrahedron_transform.set_position(glm.vec3(-6.0, 2, -2.0))
    tetrahedron.set_transform(tetrahedron_transform)

    octahedron = Octahedron(
        size_factor=2.5,
        color=glm.vec4(0.2, 0.9, 0.5, 1.0)
    )
    octahedron_transform = Transform()
    octahedron_transform.set_position(glm.vec3(-3.0, 2, -4.0))
    octahedron.set_transform(octahedron_transform)

    icosahedron = Icosahedron(
        size_factor=2.0,
        color=glm.vec4(0.9, 0.8, 0.2, 1.0)
    )
    icosahedron_transform = Transform()
    icosahedron_transform.set_position(glm.vec3(3.0, 3, -4.0))
    icosahedron.set_transform(icosahedron_transform)

    cylinder = Cylinder(
        size_factor=2.5,
        color=glm.vec4(0.3, 0.7, 0.9, 1.0)
    )
    cylinder_transform = Transform()
    cylinder_transform.set_position(glm.vec3(6.0, 2.75, -2.0))
    cylinder.set_transform(cylinder_transform)

    cone = Cone(
        size_factor=2.5,
        color=glm.vec4(0.9, 0.3, 0.6, 1.0),
        segments=256
    )
    cone_transform = Transform()
    cone_transform.set_position(glm.vec3(-6.0, 1.75, 4.0))
    cone.set_transform(cone_transform)

    cube = Cube(
        size_factor=2.5,
        cube_color=glm.vec4(0.9, 0.7, 0.6, 1.0)
    )
    cube_transform = Transform()
    cube_transform.set_position(glm.vec3(-12.0, 1.75, 4.0))
    cube.set_transform(cube_transform)

    sphere = Sphere(
        radius=5.5,
        lat_level=4,
        lon_level=4,
        sphere_color=glm.vec4(0.9, 0.3, 0.4, 1.0)
    )
    sphere_transform = Transform()
    sphere_transform.set_position(glm.vec3(14.0, 7.75, -30.0))
    sphere.set_transform(sphere_transform)

    renderer = Renderer()

    mouse_pressed = False
    last_mouse_x = 400.0
    last_mouse_y = 300.0
    camera_speed = 10

    def mouse_button_callback(window, button, action, mods):
        nonlocal mouse_pressed
        if button == glfw.MOUSE_BUTTON_LEFT:
            mouse_pressed = (action == glfw.PRESS)

    def cursor_position_callback(window, xpos, ypos):
        nonlocal last_mouse_x, last_mouse_y, camera

        if not mouse_pressed:
            last_mouse_x, last_mouse_y = xpos, ypos
            return

        x_offset = xpos - last_mouse_x
        y_offset = last_mouse_y - ypos

        last_mouse_x, last_mouse_y = xpos, ypos
        sensitivity = 0.3

        new_yaw = camera.get_yaw() + x_offset * sensitivity
        new_pitch = camera.get_pitch() + y_offset * sensitivity

        camera.set_orientation(
            new_yaw,
            new_pitch
        )

    glfw.set_mouse_button_callback(win.get_window(), mouse_button_callback)
    glfw.set_cursor_pos_callback(win.get_window(), cursor_position_callback)

    floor_size = 100
    floor_half = floor_size / 2.0
    floor_vertices = [
        Vertex(
            glm.vec3(-floor_half, 0.0, -floor_half),
            glm.vec3(0.0, 1.0, 0.0),
            glm.vec2(0.0, 0.0)
        ),
        Vertex(
            glm.vec3(floor_half, 0.0, -floor_half),
            glm.vec3(0.0, 1.0, 0.0),
            glm.vec2(1.0, 0.0)
        ),
        Vertex(
            glm.vec3(floor_half, 0.0, floor_half),
            glm.vec3(0.0, 1.0, 0.0),
            glm.vec2(1.0, 1.0)
        ),
        Vertex(
            glm.vec3(-floor_half, 0.0, floor_half),
            glm.vec3(0.0, 1.0, 0.0),
            glm.vec2(0.0, 1.0)
        ),
    ]
    floor_shader = Shader("src/shaders/floor.vert", "src/shaders/floor.frag")
    floor_material = Material(floor_shader)
    floor_indices = [0, 1, 2, 0, 2, 3]
    floor_mesh = Mesh(floor_vertices, floor_indices)
    floor_transform = Transform()
    floor_transform.set_position(glm.vec3(0.0, 0.0, 0.0))
    floor_model = Model(
        [ModelPiece(floor_mesh, floor_material, floor_transform)]
    )
    floor_entity = Entity(floor_model, floor_transform)

    while not win.should_close():
        delta_time = win.get_delta_time()

        renderer.clear()

        update(win, camera, camera_speed, delta_time)

        floor_shader.use()
        floor_shader.set_uniform("camera_pos", camera.get_position())
        renderer.render_entity(camera, floor_entity, light=None)

        hydrogen.render(renderer, camera, light)
        hydrogen.update_positions(delta_time)

        helium.render(renderer, camera, light)
        helium.update_positions(delta_time)

        carbon.render(renderer, camera, light)
        carbon.update_positions(delta_time)

        nitrogen.render(renderer, camera, light)
        nitrogen.update_positions(delta_time)

        oxygen.render(renderer, camera, light)
        oxygen.update_positions(delta_time)

        fluorine.render(renderer, camera, light)
        fluorine.update_positions(delta_time)

        neon.render(renderer, camera, light)
        neon.update_positions(delta_time)

        tetrahedron.render(renderer, camera, light)
        octahedron.render(renderer, camera, light)
        icosahedron.render(renderer, camera, light)
        cylinder.render(renderer, camera, light)
        cone.render(renderer, camera, light)
        cube.render(renderer, camera, light)
        sphere.render(renderer, camera, light)

        electron_cloud.render(renderer, camera, light)
        electron_cloud.update_positions(delta_time)

        win.swap_buffers()
        win.poll_events()

    win.destroy()
    glfw.terminate()
    return 0


if __name__ == "__main__":
    main()
