import glfw
import OpenGL.GL as gl
import glm

from window import Window
from camera import Camera
from renderer import Renderer

from vision import Vision


def main():
    win = Window(800, 600, "VESPR - Visualizer")
    if win.init_backend() != 0 or win.init() != 0:
        return 1
    win.set_visible(True)
    gl.glEnable(gl.GL_DEPTH_TEST)
    gl.glClearColor(0.0, 0.0, 0.0, 1.0)

    # câmera existe só pra manter a estrutura (não é usada no bg)
    camera = Camera(
        position=glm.vec3(0.0, 2.0, 10.0),
        world_up=glm.vec3(0.0, 1.0, 0.0),
        yaw=-90.0,
        pitch=0.0,
        aspect=win.get_aspect_ratio()
    )

    renderer = Renderer()

    vision = Vision(camera_id=0)
    try:
        vision.open()
    except RuntimeError as e:
        print("erro ao abrir câmera:", e)
        win.destroy()
        glfw.terminate()
        return 1

    while not win.should_close():
        renderer.clear()

        # só o background da câmera
        vision.update_camera_background(aspect_ratio=win.get_aspect_ratio())

        win.swap_buffers()
        win.poll_events()

    vision.close()
    win.destroy()
    glfw.terminate()
    return 0


if __name__ == "__main__":
    main()
