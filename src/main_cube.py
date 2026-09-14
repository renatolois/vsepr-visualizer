import glfw
import OpenGL.GL as gl
import glm
import numpy as np

from window import Window
from camera import Camera
from vision import Vision
from polygons.tetrahedron import Tetrahedron      # <-- trocado
from renderer import Renderer
from light import Light
from shader import Shader
from transform import Transform


TAG_DEBUG_CUBE = 20
TAG_SIZE_METERS = 0.02


# ---------------------------------------------------------------------------
# Eixos de debug: desenha X (vermelho), Y (verde), Z (azul) na origem
# do transform passado. Usa GL_LINES com um shader "flat" (sem luz).
# ---------------------------------------------------------------------------
class DebugAxes:
    def __init__(self, length: float = 0.03):
        self.length = length

        self.shader = Shader(
            "src/testes-IA-main/axes.vert",
            "src/testes-IA-main/axes.frag",
        )

        self._axes = []

        colors = [
            glm.vec4(1.0, 0.0, 0.0, 1.0),  # X vermelho
            glm.vec4(0.0, 1.0, 0.0, 1.0),  # Y verde
            glm.vec4(0.0, 0.0, 1.0, 1.0),  # Z azul
        ]
        directions = [
            glm.vec3(1.0, 0.0, 0.0),
            glm.vec3(0.0, 1.0, 0.0),
            glm.vec3(0.0, 0.0, 1.0),
        ]

        for direction, color in zip(directions, colors):
            verts = np.array([
                0.0, 0.0, 0.0,
                direction.x * length,
                direction.y * length,
                direction.z * length,
            ], dtype=np.float32)

            vao = gl.glGenVertexArrays(1)
            vbo = gl.glGenBuffers(1)

            gl.glBindVertexArray(vao)
            gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo)
            gl.glBufferData(gl.GL_ARRAY_BUFFER, verts.nbytes,
                            verts, gl.GL_STATIC_DRAW)

            gl.glEnableVertexAttribArray(0)
            gl.glVertexAttribPointer(0, 3, gl.GL_FLOAT, gl.GL_FALSE,
                                     3 * 4, gl.ctypes.c_void_p(0))

            gl.glBindVertexArray(0)
            gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)

            self._axes.append((vao, vbo, color))

        self.model_matrix = glm.mat4(1.0)

    def set_transform(self, transform: Transform) -> None:
        self.model_matrix = transform.get_model_matrix()

    def render(self, camera: Camera) -> None:
        self.shader.use()
        self.shader.set_uniform("material_transform", self.model_matrix)
        self.shader.set_uniform(
            "material_camera_view", camera.get_view_matrix())
        self.shader.set_uniform(
            "material_camera_projection", camera.get_projection_matrix())

        for vao, _vbo, color in self._axes:
            self.shader.set_uniform("material_color", color)
            gl.glBindVertexArray(vao)
            gl.glDrawArrays(gl.GL_LINES, 0, 2)
            gl.glBindVertexArray(0)


def print_marker_pose(pos: glm.vec3, rot: glm.quat, frame_id: int) -> None:
    if frame_id % 30 != 0:
        return
    print(
        f"[{frame_id:6d}] "
        f"pos=({pos.x:+.4f}, {pos.y:+.4f}, {pos.z:+.4f})  "
        f"quat=(w={rot.w:+.3f}, x={rot.x:+.3f}, "
        f"y={rot.y:+.3f}, z={rot.z:+.3f})"
    )


def main():
    win = Window(800, 600, "Marker Debug")
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

    vision = Vision(camera_id=0)
    vision.open()

    # Tetraedro em vez do cubo
    tetra = Tetrahedron(TAG_SIZE_METERS, glm.vec4(0.9, 0.5, 0.1, 1.0))
    renderer = Renderer()

    axes = DebugAxes(length=0.03)

    frame_id = 0

    # -----------------------------------------------------------------------
    # MODO DE TESTE
    # -----------------------------------------------------------------------
    # CUBO A: acima e à frente (testa Y e Z)
    test_tetra_a = Transform(
        position=glm.vec3(0.0, 0.10, -0.30),
        rotation=glm.quat(1, 0, 0, 0),
        scale=glm.vec3(1, 1, 1),
    )

    # CUBO B: à direita e à frente (testa X e Z)
    test_tetra_b = Transform(
        position=glm.vec3(0.10, 0.0, -0.30),
        rotation=glm.quat(1, 0, 0, 0),
        scale=glm.vec3(1, 1, 1),
    )

    # Eixos fixos em (0, 0, -0.5) sem rotação
    test_axes = Transform(
        position=glm.vec3(0.0, 0.0, -0.50),
        rotation=glm.quat(1, 0, 0, 0),
        scale=glm.vec3(1, 1, 1),
    )

    # Flags de debug
    DEBUG_TEST_TETRAS = True
    DEBUG_TEST_AXES = True
    DEBUG_MARKER = True

    while not win.should_close():
        gl.glClear(gl.GL_DEPTH_BUFFER_BIT | gl.GL_COLOR_BUFFER_BIT)

        gl.glDisable(gl.GL_DEPTH_TEST)
        vision.update_camera_background(win.get_aspect_ratio())
        gl.glEnable(gl.GL_DEPTH_TEST)

        # -------------------------------------------------------------------
        # 1) Testes fixos
        # -------------------------------------------------------------------
        if DEBUG_TEST_TETRAS:
            tetra.set_transform(test_tetra_a)
            tetra.render(renderer, camera, light)

            tetra.set_transform(test_tetra_b)
            tetra.render(renderer, camera, light)

        if DEBUG_TEST_AXES:
            axes.set_transform(test_axes)
            gl.glDisable(gl.GL_DEPTH_TEST)
            axes.render(camera)
            gl.glEnable(gl.GL_DEPTH_TEST)

        # -------------------------------------------------------------------
        # 2) Marcador
        # -------------------------------------------------------------------
        if DEBUG_MARKER:
            frame = vision.get_framebuffer()
            if frame is not None:
                vision.detect_markers()

                if TAG_DEBUG_CUBE in vision.tag_IDs:
                    idx = vision.tag_IDs.index(TAG_DEBUG_CUBE)
                    corners = vision.tags_corners[idx]

                    marker_transform = vision.get_marker_transform(
                        corners,
                        camera,
                        float(frame.shape[1]),
                        float(frame.shape[0]),
                        TAG_SIZE_METERS
                    )

                    pos = marker_transform.get_position()
                    rot = marker_transform.get_rotation()
                    print_marker_pose(pos, rot, frame_id)

                    # Eixos do marcador
                    axes.set_transform(marker_transform)
                    gl.glDisable(gl.GL_DEPTH_TEST)
                    axes.render(camera)
                    gl.glEnable(gl.GL_DEPTH_TEST)

                    # Tetraedro no marcador
                    tetra.set_transform(marker_transform)
                    tetra.render(renderer, camera, light)

        win.swap_buffers()
        win.poll_events()
        frame_id += 1

    vision.close()
    win.destroy()
    glfw.terminate()
    return 0


if __name__ == "__main__":
    main()
