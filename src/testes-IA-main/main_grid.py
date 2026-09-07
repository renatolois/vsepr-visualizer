import glfw
import OpenGL.GL as gl
import glm
import math

from window import Window
from polygons.sphere import Sphere          # <-- sua classe Sphere
from shader import Shader
from camera import Camera
from transform import Transform
from entity import Entity
from model import Model, ModelPiece
from mesh import Mesh
from material import Material
from vertex import Vertex
from renderer import Renderer
from light import Light


def create_floor_entity(size=100.0):
    """Cria uma entidade de chão com um grande plano."""
    half = size / 2.0
    vertices = [
        Vertex(glm.vec3(-half, 0.0, -half), glm.vec3(0.0, 1.0, 0.0), glm.vec2(0.0, 0.0)),
        Vertex(glm.vec3( half, 0.0, -half), glm.vec3(0.0, 1.0, 0.0), glm.vec2(1.0, 0.0)),
        Vertex(glm.vec3( half, 0.0,  half), glm.vec3(0.0, 1.0, 0.0), glm.vec2(1.0, 1.0)),
        Vertex(glm.vec3(-half, 0.0,  half), glm.vec3(0.0, 1.0, 0.0), glm.vec2(0.0, 1.0)),
    ]
    indices = [0, 1, 2, 0, 2, 3]
    mesh = Mesh(vertices, indices)
    transform = Transform()
    transform.set_position(glm.vec3(0.0, 0.0, 0.0))
    # O material será criado depois com o shader do grid
    model = Model([ModelPiece(mesh, Material(), transform)])
    entity = Entity(model, transform)
    return entity, mesh


def main():
    # 1. Janela
    win = Window(800, 600, "VESPR - Grid Infinito (Engine)")
    if win.init_backend() != 0 or win.init() != 0:
        return 1
    win.set_visible(True)
    gl.glEnable(gl.GL_DEPTH_TEST)
    gl.glClearColor(0.0, 0.0, 0.0, 1.0)

    # 2. Câmera orbital
    camera = Camera(
        position=glm.vec3(3.0, 0.0, 0.0),
        world_up=glm.vec3(0.0, 1.0, 0.0),
        yaw=-90.0,
        pitch=0.0,
        aspect=win.get_aspect_ratio()
    )

    # 3. Luz
    light = Light(glm.vec3(1.0, 1.0, 1.0), 1.5)
    light.set_translation(glm.vec3(20.0, 3.0, 4.0))

    # 4. Esfera (usando a classe Sphere existente)
    #    Cria uma esfera com raio 1.0, níveis 4 e 4, e cor azul clara
    sphere = Sphere(radius=1.0, lat_level=4, lon_level=4, sphere_color=glm.vec4(0.2, 0.6, 0.9, 1.0))
    # Coloca a esfera um pouco acima do chão
    sphere_transform = Transform()
    sphere_transform.set_position(glm.vec3(0.0, 1.0, 0.0))
    sphere.set_transform(sphere_transform)

    # 5. Chão (grid)
    floor_shader = Shader("src/shaders/grid.vert", "src/shaders/grid.frag")
    floor_entity, floor_mesh = create_floor_entity(100.0)
    floor_material = Material(floor_shader)
    floor_material.set_color(glm.vec4(1.0, 1.0, 1.0, 1.0))  # não usado, mas evita warnings
    floor_piece = floor_entity.get_model().get_model_pieces()[0]
    floor_piece.material = floor_material

    renderer = Renderer()

    # 6. Controles do mouse (orbit)
    mouse_pressed = False
    last_mouse_x = 400.0
    last_mouse_y = 300.0
    camera_yaw = -90.0
    camera_pitch = 0.0
    camera_distance = 3.0

    def mouse_button_callback(window, button, action, mods):
        nonlocal mouse_pressed
        if button == glfw.MOUSE_BUTTON_LEFT:
            mouse_pressed = (action == glfw.PRESS)

    def cursor_position_callback(window, xpos, ypos):
        nonlocal last_mouse_x, last_mouse_y, camera_yaw, camera_pitch
        if not mouse_pressed:
            last_mouse_x, last_mouse_y = xpos, ypos
            return
        x_offset = xpos - last_mouse_x
        y_offset = last_mouse_y - ypos
        last_mouse_x, last_mouse_y = xpos, ypos
        sensitivity = 0.3
        camera_yaw += x_offset * sensitivity
        camera_pitch -= y_offset * sensitivity
        camera_pitch = max(-89.0, min(89.0, camera_pitch))

    glfw.set_mouse_button_callback(win.get_window(), mouse_button_callback)
    glfw.set_cursor_pos_callback(win.get_window(), cursor_position_callback)

    # 7. Loop principal
    while not win.should_close():
        renderer.clear()

        # Atualiza câmera (órbita)
        rad_yaw = glm.radians(camera_yaw)
        rad_pitch = glm.radians(camera_pitch)
        cam_x = camera_distance * math.cos(rad_pitch) * math.cos(rad_yaw)
        cam_y = camera_distance * math.sin(rad_pitch)
        cam_z = camera_distance * math.cos(rad_pitch) * math.sin(rad_yaw)
        camera.set_position(glm.vec3(cam_x, cam_y, cam_z))
        camera.set_target(glm.vec3(0.0, 0.0, 0.0))
        camera.set_aspect(win.get_aspect_ratio())

        # --- Renderiza o chão (grid) ---
        floor_shader.use()
        floor_shader.set_uniform("CameraPos", camera.get_position())
        renderer.render_entity(camera, floor_entity, light=None)

        # --- Renderiza a esfera (usando a classe Sphere) ---
        sphere.render(renderer, camera, light)

        win.swap_buffers()
        win.poll_events()

    win.destroy()
    glfw.terminate()
    return 0


if __name__ == "__main__":
    main()
