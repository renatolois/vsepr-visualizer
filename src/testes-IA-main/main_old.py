import glfw
import OpenGL.GL as gl
import glm
import math

from window import Window
from polygons.sphere import Sphere
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


def main():
    # 1. Inicializa a janela
    win = Window(800, 600, "VESPR-Visualizer - Camera Orbit")
    if win.init_backend() != 0 or win.init() != 0:
        return 1

    win.set_visible(True)
    gl.glEnable(gl.GL_DEPTH_TEST)
    gl.glEnable(gl.GL_MULTISAMPLE)
    gl.glClearColor(0.1, 0.1, 0.1, 1.0)

    # 2. Cria o shader (deve existir em src/shaders/vertex.vert e fragment.frag)
    shader = Shader("src/shaders/vertex.vert", "src/shaders/fragment.frag")

    # 3. Câmera orbital (igual ao C++)
    camera = Camera(
        position=glm.vec3(3.0, 0.0, 0.0),
        world_up=glm.vec3(0.0, 1.0, 0.0),
        yaw=-90.0,
        pitch=0.0,
        aspect=win.get_aspect_ratio()
    )

    # 4. Luz (igual ao C++)
    light = Light(glm.vec3(1.0, 1.0, 1.0), 1.5)
    light.set_translation(glm.vec3(2.0, 3.0, 4.0))

    # 5. Cria a esfera (dados)
    sphere_data = Sphere.get_vertices_and_indices(radius=1.0, lat_level=4, lon_level=4)
    vertices = [Vertex(v.position, v.normal, v.tex_coords) for v in sphere_data.vertices]
    mesh = Mesh(vertices, sphere_data.indices)

    # 6. Material: usa o shader, define a cor via set_color (NÃO use set_uniform)
    material = Material(shader)
    material.set_color(glm.vec4(0.2, 0.6, 0.9, 1.0))   # <-- corrigido
    # Opcional: material.set_shininess(32.0)

    # 7. Transform, Model, Entity (igual ao C++)
    transform = Transform()
    model = Model([ModelPiece(mesh, material, transform)])
    entity = Entity(model, transform)

    renderer = Renderer()

    # 8. Controle do mouse para órbita (mesmo código que funcionava)
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

    # 9. Loop principal
    while not win.should_close():
        renderer.clear()

        # Atualiza posição da câmera (órbita)
        rad_yaw = glm.radians(camera_yaw)
        rad_pitch = glm.radians(camera_pitch)
        cam_x = camera_distance * math.cos(rad_pitch) * math.cos(rad_yaw)
        cam_y = camera_distance * math.sin(rad_pitch)
        cam_z = camera_distance * math.cos(rad_pitch) * math.sin(rad_yaw)
        camera.set_position(glm.vec3(cam_x, cam_y, cam_z))
        camera.set_target(glm.vec3(0.0, 0.0, 0.0))
        camera.set_aspect(win.get_aspect_ratio())

        # Renderiza a entidade com a luz (o renderer chama material.apply() internamente)
        renderer.render_entity(camera, entity, light)

        win.swap_buffers()
        win.poll_events()

    # 10. Limpeza (opcional, mas evita o erro do __del__)
    # Se quiser, pode chamar explícitamente gl.glDeleteProgram, etc.
    win.destroy()
    glfw.terminate()
    return 0


if __name__ == "__main__":
    main()
