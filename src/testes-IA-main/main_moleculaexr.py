import cv2
import numpy as np
import glm
import OpenGL.GL as gl
from typing import List, Dict
import ctypes

from window import Window
from vision import Vision
from camera import Camera
from renderer import Renderer
from light import Light
from transform import Transform
from hydrogen import Hydrogen
from oxygen import Oxygen
from atom_utils import verify_distance_higher_than
from atom_constants import *
from polygons.sphere import Sphere
from polygons.cube import Cube


# ============================================================
# Estrutura DetectedTag (equivalente ao struct do C++)
# ============================================================
class DetectedTag:
    def __init__(self, tag_id: int = -1):
        self.id: int = tag_id
        self.current_marker_transform: Transform = Transform()
        self.last_marker_transform: Transform = Transform()
        self.active: bool = False
        self.time_since_lost: float = 999.0


# ============================================================
# Função auxiliar para renderizar átomo (macro RENDER_ATOM)
# ============================================================
def render_atom(tag_id: int, atom, detected_tags: Dict[int, DetectedTag],
                renderer: Renderer, camera: Camera, light: Light, delta_time: float):
    if detected_tags[tag_id].active:
        smooth_transform = Transform.smooth_transform(
            detected_tags[tag_id].last_marker_transform,
            detected_tags[tag_id].current_marker_transform,
            25.0,
            delta_time
        )
        atom.atom_sphere.set_transform(smooth_transform)
        atom.atom_sphere.render(renderer, camera, light)


# ============================================================
# Funções para compilar shaders (sem usar a classe Shader)
# ============================================================
def compile_shader(source: str, shader_type: int) -> int:
    shader = gl.glCreateShader(shader_type)
    gl.glShaderSource(shader, source)
    gl.glCompileShader(shader)
    success = gl.glGetShaderiv(shader, gl.GL_COMPILE_STATUS)
    if not success:
        info_log = gl.glGetShaderInfoLog(shader)
        raise RuntimeError(f"Shader compilation error:\n{info_log}")
    return shader


def create_program(vert_src: str, frag_src: str) -> int:
    vert = compile_shader(vert_src, gl.GL_VERTEX_SHADER)
    frag = compile_shader(frag_src, gl.GL_FRAGMENT_SHADER)
    program = gl.glCreateProgram()
    gl.glAttachShader(program, vert)
    gl.glAttachShader(program, frag)
    gl.glLinkProgram(program)
    success = gl.glGetProgramiv(program, gl.GL_LINK_STATUS)
    if not success:
        info_log = gl.glGetProgramInfoLog(program)
        raise RuntimeError(f"Program linking error:\n{info_log}")
    gl.glDeleteShader(vert)
    gl.glDeleteShader(frag)
    return program


# ============================================================
# Função initialize (equivalente à do C++)
# ============================================================
def initialize(window: Window, vision: Vision):
    vision.open()
    window.init_backend()
    window.init()
    window.set_visible(True)
    gl.glEnable(gl.GL_DEPTH_TEST)
    gl.glClearColor(0.01, 0.03, 0.1, 1.0)


# ============================================================
# MAIN
# ============================================================
def main():
    # Arrays de ligações químicas
    chemical_bonds = [False] * NUM_TOTAL_CHEMICAL_BONDS
    for i in range(NUM_TOTAL_CHEMICAL_BONDS):
        chemical_bonds[i] = False

    # Detected tags
    MAX_TAGS = MAX_TAGS_APRILTAG_36H11 + 15
    detected_tags: Dict[int, DetectedTag] = {}
    for i in range(MAX_TAGS):
        detected_tags[i] = DetectedTag(i)

    last_tag_ids: List[int] = []
    active_not_detected_tags = [0] * MAX_TAGS
    num_active_not_detected_tags = 0

    h0_anim_position = glm.vec3(0.0)
    h1_anim_position = glm.vec3(0.0)
    was_bonded_last_frame = False

    # Cria janela
    WINDOW_WIDTH, WINDOW_HEIGHT = 640, 480
    window = Window(WINDOW_WIDTH, WINDOW_HEIGHT, "MoleculaeXR")

    # Inicializa Vision
    vision = Vision(0, cv2.aruco.DICT_APRILTAG_36h11)

    # Configura parâmetros do detector ArUco
    aruco_params = vision.get_aruco_params()
    aruco_params.cornerRefinementMethod = cv2.aruco.CORNER_REFINE_SUBPIX
    aruco_params.cornerRefinementWinSize = 5
    aruco_params.cornerRefinementMaxIterations = 30
    aruco_params.cornerRefinementMinAccuracy = 0.1
    aruco_params.adaptiveThreshWinSizeMin = 3
    aruco_params.adaptiveThreshWinSizeMax = 23
    aruco_params.adaptiveThreshWinSizeStep = 4
    aruco_params.minMarkerPerimeterRate = 0.02
    aruco_params.maxMarkerPerimeterRate = 4.0
    aruco_params.errorCorrectionRate = 0.6
    vision.set_aruco_params(aruco_params)

    # Chama initialize (abre a câmera, configura OpenGL)
    initialize(window, vision)

    # Cria renderer, câmera AR e luz
    renderer = Renderer()
    ar_camera = Camera()
    ar_camera.set_position(glm.vec3(0, 0, 0))
    ar_camera.set_aspect(WINDOW_WIDTH / WINDOW_HEIGHT)
    ar_camera.set_zoom(60.0)
    ar_camera.set_near(0.001)
    ar_camera.set_far(10.0)

    light = Light(glm.vec3(1.0, 1.0, 1.0), 1.0)
    light.translate_xyz(0.0, 5.0, 0.0)

    # Cria átomos
    hydrogen_0 = Hydrogen(MOLECULAEXR_TAG_ID_HYDROGEN_0, TAG_SIZE_METERS, 4, 4)
    hydrogen_1 = Hydrogen(MOLECULAEXR_TAG_ID_HYDROGEN_1, TAG_SIZE_METERS, 4, 4)
    oxygen_0 = Oxygen(MOLECULAEXR_TAG_ID_OXYGEN_0, TAG_SIZE_METERS, 4, 4)

    # Objetos de debug
    cube = Cube(TAG_SIZE_METERS)
    sphere = Sphere(TAG_SIZE_METERS / 2, 3, 3)

    # ============================================================
    # CONFIGURAÇÃO DO FUNDO DA WEBCAM (shaders + geometria)
    # ============================================================
    # Shaders para textura (sem projeção, em NDC)
    bg_vertex_shader_source = """
    #version 330 core
    layout (location = 0) in vec2 aPos;
    layout (location = 1) in vec2 aTexCoord;
    out vec2 TexCoord;
    void main() {
        gl_Position = vec4(aPos.x, aPos.y, 0.0, 1.0);
        TexCoord = aTexCoord;
    }
    """
    bg_fragment_shader_source = """
    #version 330 core
    in vec2 TexCoord;
    uniform sampler2D uTexture;
    out vec4 FragColor;
    void main() {
        FragColor = texture(uTexture, TexCoord);
    }
    """

    bg_program = create_program(bg_vertex_shader_source, bg_fragment_shader_source)
    u_texture_loc = gl.glGetUniformLocation(bg_program, "uTexture")

    # Vértices e índices do quad (NDC)
    quad_vertices = np.array([
        -1.0, -1.0, 0.0, 0.0,
         1.0, -1.0, 1.0, 0.0,
         1.0,  1.0, 1.0, 1.0,
        -1.0,  1.0, 0.0, 1.0
    ], dtype=np.float32)
    quad_indices = np.array([0, 1, 2, 0, 2, 3], dtype=np.uint32)

    # VAO, VBO, EBO
    vao = gl.glGenVertexArrays(1)
    gl.glBindVertexArray(vao)

    vbo = gl.glGenBuffers(1)
    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo)
    gl.glBufferData(gl.GL_ARRAY_BUFFER, quad_vertices.nbytes, quad_vertices, gl.GL_STATIC_DRAW)

    ebo = gl.glGenBuffers(1)
    gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, ebo)
    gl.glBufferData(gl.GL_ELEMENT_ARRAY_BUFFER, quad_indices.nbytes, quad_indices, gl.GL_STATIC_DRAW)

    # Atributos: posição (2 floats) e texCoord (2 floats)
    stride = 4 * ctypes.sizeof(ctypes.c_float)
    gl.glVertexAttribPointer(0, 2, gl.GL_FLOAT, gl.GL_FALSE, stride, ctypes.c_void_p(0))
    gl.glEnableVertexAttribArray(0)
    gl.glVertexAttribPointer(1, 2, gl.GL_FLOAT, gl.GL_FALSE, stride, ctypes.c_void_p(2 * ctypes.sizeof(ctypes.c_float)))
    gl.glEnableVertexAttribArray(1)

    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)
    gl.glBindVertexArray(0)

    # Cria textura para o fundo
    texture_id = gl.glGenTextures(1)
    gl.glBindTexture(gl.GL_TEXTURE_2D, texture_id)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP_TO_EDGE)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP_TO_EDGE)

    # ============================================================
    # LOOP PRINCIPAL
    # ============================================================
    while not window.should_close():
        window.poll_events()
        delta_time = window.get_delta_time()

        # Limpa tela
        gl.glClearColor(0.01, 0.03, 0.1, 1.0)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

        # ---- 1. Renderiza o fundo da webcam (sem depth test) ----
        # Equivalente a: glDisable(GL_DEPTH_TEST); vision.update_camera_background(ar_camera->get_aspect()); glEnable(GL_DEPTH_TEST);
        gl.glDisable(gl.GL_DEPTH_TEST)
        vision.read()
        frame = vision.get_framebuffer()
        if frame is not None:
            # Converte e carrega a textura
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_flipped = np.flipud(frame_rgb)
            gl.glBindTexture(gl.GL_TEXTURE_2D, texture_id)
            gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGB, WINDOW_WIDTH, WINDOW_HEIGHT, 0,
                            gl.GL_RGB, gl.GL_UNSIGNED_BYTE, frame_flipped)

            # Desenha o quad com shader
            gl.glUseProgram(bg_program)
            gl.glUniform1i(u_texture_loc, 0)
            gl.glBindVertexArray(vao)
            gl.glActiveTexture(gl.GL_TEXTURE0)
            gl.glBindTexture(gl.GL_TEXTURE_2D, texture_id)
            gl.glDrawElements(gl.GL_TRIANGLES, 6, gl.GL_UNSIGNED_INT, ctypes.c_void_p(0))
            gl.glBindVertexArray(0)
        gl.glEnable(gl.GL_DEPTH_TEST)

        # ---- 2. Detecta marcadores ----
        # Equivalente a: vision.detect_markers(); num_detected_tags = ...;
        vision.detect_markers()  # garante que tag_IDs seja uma lista (vazia se nada)
        num_detected = min(len(vision.tag_IDs), MAX_TAGS)
        for i in range(num_detected):
            tag_id = vision.tag_IDs[i]
            new_last = detected_tags[tag_id].current_marker_transform
            new_current = vision.get_marker_transform(
                vision.tags_corners[i],
                ar_camera,
                float(frame.shape[1]),
                float(frame.shape[0]),
                TAG_SIZE_METERS
            )
            new_current.translate_local(glm.vec3(0.0, 0.0, TAG_SIZE_METERS))

            # Atualiza a estrutura detected_tags
            detected_tags[tag_id].current_marker_transform = new_current
            detected_tags[tag_id].last_marker_transform = new_last
            detected_tags[tag_id].active = True
            detected_tags[tag_id].time_since_lost = 0.0

        # ---- 3. Verifica quem sumiu (algoritmo O(n*m)) ----
        num_active_not_detected_tags = 0
        for marker_id in last_tag_ids:
            if marker_id not in vision.tag_IDs:
                detected_tags[marker_id].time_since_lost += delta_time
                if detected_tags[marker_id].time_since_lost > MAX_LOST_TIME_TOLERATION:
                    detected_tags[marker_id].active = False
                else:
                    active_not_detected_tags[num_active_not_detected_tags] = marker_id
                    num_active_not_detected_tags += 1

        # ---- 4. Verifica quem apareceu que não havia antes ----
        for marker_id in vision.tag_IDs:
            if marker_id not in last_tag_ids:
                detected_tags[marker_id].active = True
                detected_tags[marker_id].time_since_lost = 0.0
                detected_tags[marker_id].last_marker_transform = detected_tags[marker_id].current_marker_transform

        # Atualiza lista de IDs para o próximo frame
        last_tag_ids = vision.tag_IDs.copy()
        for i in range(num_active_not_detected_tags):
            last_tag_ids.append(active_not_detected_tags[i])

        # ---- 5. Renderiza cubo de debug ----
        if detected_tags[TAG_DEBUG_CUBE].active:
            smooth_transform = Transform.smooth_transform(
                detected_tags[TAG_DEBUG_CUBE].last_marker_transform,
                detected_tags[TAG_DEBUG_CUBE].current_marker_transform,
                25.0,
                delta_time
            )
            cube.set_transform(smooth_transform)
            cube.render(renderer, ar_camera, light)

        # ---- 6. Lógica de ligação química (H2O) ----
        h0_active = detected_tags[MOLECULAEXR_TAG_ID_HYDROGEN_0].active
        h1_active = detected_tags[MOLECULAEXR_TAG_ID_HYDROGEN_1].active
        o0_active = detected_tags[MOLECULAEXR_TAG_ID_OXYGEN_0].active

        if h0_active and h1_active and o0_active:
            if not chemical_bonds[H0_H1_O0_TO_H2O_INDEX]:
                dist_h0_o0_bad = verify_distance_higher_than(
                    detected_tags[MOLECULAEXR_TAG_ID_HYDROGEN_0].current_marker_transform,
                    detected_tags[MOLECULAEXR_TAG_ID_OXYGEN_0].current_marker_transform,
                    MIN_HYDROGEN_OXYGEN_DIST_TO_H2O
                )
                dist_h1_o0_bad = verify_distance_higher_than(
                    detected_tags[MOLECULAEXR_TAG_ID_HYDROGEN_1].current_marker_transform,
                    detected_tags[MOLECULAEXR_TAG_ID_OXYGEN_0].current_marker_transform,
                    MIN_HYDROGEN_OXYGEN_DIST_TO_H2O
                )
                if not (dist_h0_o0_bad or dist_h1_o0_bad):
                    chemical_bonds[H0_H1_O0_TO_H2O_INDEX] = True
            else:
                dist_h0_o0_bad = verify_distance_higher_than(
                    detected_tags[MOLECULAEXR_TAG_ID_HYDROGEN_0].current_marker_transform,
                    detected_tags[MOLECULAEXR_TAG_ID_OXYGEN_0].current_marker_transform,
                    MIN_HYDROGEN_OXYGEN_DIST_TO_H2O_PLUS_DELTA
                )
                dist_h1_o0_bad = verify_distance_higher_than(
                    detected_tags[MOLECULAEXR_TAG_ID_HYDROGEN_1].current_marker_transform,
                    detected_tags[MOLECULAEXR_TAG_ID_OXYGEN_0].current_marker_transform,
                    MIN_HYDROGEN_OXYGEN_DIST_TO_H2O_PLUS_DELTA
                )
                if dist_h0_o0_bad or dist_h1_o0_bad:
                    chemical_bonds[H0_H1_O0_TO_H2O_INDEX] = False
        else:
            chemical_bonds[H0_H1_O0_TO_H2O_INDEX] = False

        # ---- 7. Animação de posição ao ligar ----
        if chemical_bonds[H0_H1_O0_TO_H2O_INDEX] and not was_bonded_last_frame:
            h0_anim_position = detected_tags[MOLECULAEXR_TAG_ID_HYDROGEN_0].current_marker_transform.get_position()
            h1_anim_position = detected_tags[MOLECULAEXR_TAG_ID_HYDROGEN_1].current_marker_transform.get_position()
        was_bonded_last_frame = chemical_bonds[H0_H1_O0_TO_H2O_INDEX]

        # ---- 8. Renderização dos átomos ----
        if not chemical_bonds[H0_H1_O0_TO_H2O_INDEX]:
            # Estado não ligado (cores originais)
            hydrogen_0.set_color(Transform.smooth_color(hydrogen_0.get_color(), HYDROGEN_SPHERE_COLOR, 3.5, delta_time))
            hydrogen_1.set_color(Transform.smooth_color(hydrogen_1.get_color(), HYDROGEN_SPHERE_COLOR, 3.5, delta_time))
            oxygen_0.set_color(Transform.smooth_color(oxygen_0.get_color(), OXYGEN_SPHERE_COLOR, 3.5, delta_time))

            if h0_active:
                render_atom(MOLECULAEXR_TAG_ID_HYDROGEN_0, hydrogen_0, detected_tags, renderer, ar_camera, light, delta_time)
            if h1_active:
                render_atom(MOLECULAEXR_TAG_ID_HYDROGEN_1, hydrogen_1, detected_tags, renderer, ar_camera, light, delta_time)
            if o0_active:
                render_atom(MOLECULAEXR_TAG_ID_OXYGEN_0, oxygen_0, detected_tags, renderer, ar_camera, light, delta_time)
        else:
            # Estado ligado (H2O) – cores da molécula e aproximação dos hidrogênios
            hydrogen_0.set_color(Transform.smooth_color(hydrogen_0.get_color(), H2O_MOLECULE_COLOR, 2.0, delta_time))
            hydrogen_1.set_color(Transform.smooth_color(hydrogen_1.get_color(), H2O_MOLECULE_COLOR, 2.0, delta_time))
            oxygen_0.set_color(Transform.smooth_color(oxygen_0.get_color(), H2O_MOLECULE_COLOR, 2.0, delta_time))

            # Renderiza oxigênio na posição real
            render_atom(MOLECULAEXR_TAG_ID_OXYGEN_0, oxygen_0, detected_tags, renderer, ar_camera, light, delta_time)

            # Puxa hidrogênios em direção ao oxigênio
            oxygen_pos = oxygen_0.atom_sphere.get_transform().get_position()
            pull_factor = 0.5

            # Hidrogênio 0
            h0_transform = detected_tags[MOLECULAEXR_TAG_ID_HYDROGEN_0].current_marker_transform
            h0_pos = h0_transform.get_position()
            h0_transform.set_position(glm.mix(h0_pos, oxygen_pos, pull_factor))
            h0_smoothed = Transform.smooth_transform(
                hydrogen_0.atom_sphere.get_transform(),
                h0_transform,
                15.0,
                delta_time
            )
            hydrogen_0.atom_sphere.set_transform(h0_smoothed)
            hydrogen_0.atom_sphere.render(renderer, ar_camera, light)

            # Hidrogênio 1
            h1_transform = detected_tags[MOLECULAEXR_TAG_ID_HYDROGEN_1].current_marker_transform
            h1_pos = h1_transform.get_position()
            h1_transform.set_position(glm.mix(h1_pos, oxygen_pos, pull_factor))
            h1_smoothed = Transform.smooth_transform(
                hydrogen_1.atom_sphere.get_transform(),
                h1_transform,
                15.0,
                delta_time
            )
            hydrogen_1.atom_sphere.set_transform(h1_smoothed)
            hydrogen_1.atom_sphere.render(renderer, ar_camera, light)

        # ---- 9. Swap buffers ----
        window.swap_buffers()

    # ---- Fim: libera recursos ----
    vision.close()
    gl.glDeleteTextures([texture_id])
    gl.glDeleteVertexArrays(1, [vao])
    gl.glDeleteBuffers(1, [vbo])
    gl.glDeleteBuffers(1, [ebo])
    gl.glDeleteProgram(bg_program)
    window.close()


if __name__ == "__main__":
    main()
