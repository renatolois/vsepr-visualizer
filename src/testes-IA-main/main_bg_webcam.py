import cv2
import numpy as np
import glfw
from OpenGL.GL import *
from OpenGL.GLU import *

# Dimensões da câmera
CAM_WIDTH, CAM_HEIGHT = 640, 480

# Inicializa GLFW
if not glfw.init():
    raise RuntimeError("Falha ao inicializar GLFW")

# Cria janela
window = glfw.create_window(CAM_WIDTH, CAM_HEIGHT, "Camera Feed", None, None)
if not window:
    glfw.terminate()
    raise RuntimeError("Falha ao criar janela")

glfw.make_context_current(window)

# Configura viewport e projeção ortográfica
glViewport(0, 0, CAM_WIDTH, CAM_HEIGHT)
glMatrixMode(GL_PROJECTION)
glLoadIdentity()
gluOrtho2D(-1, 1, -1, 1)
glMatrixMode(GL_MODELVIEW)

# Habilita texturas
glEnable(GL_TEXTURE_2D)

# Cria textura
texture_id = glGenTextures(1)
glBindTexture(GL_TEXTURE_2D, texture_id)
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_BORDER)
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_BORDER)

# Abre a câmera
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAM_WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAM_HEIGHT)

# Opções do ArUco (opcional)
aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_250)
aruco_params = cv2.aruco.DetectorParameters()

def load_texture_from_frame(frame):
    """Converte frame BGR para RGB e carrega como textura OpenGL."""
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame_flipped = np.flipud(frame_rgb)          # OpenGL espera origem inferior esquerda
    glBindTexture(GL_TEXTURE_2D, texture_id)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, CAM_WIDTH, CAM_HEIGHT, 0, GL_RGB, GL_UNSIGNED_BYTE, frame_flipped)

def draw_quad():
    """Desenha um quadriculado com a textura."""
    glBegin(GL_QUADS)
    glTexCoord2f(0.0, 0.0); glVertex2f(-1.0, -1.0)
    glTexCoord2f(1.0, 0.0); glVertex2f( 1.0, -1.0)
    glTexCoord2f(1.0, 1.0); glVertex2f( 1.0,  1.0)
    glTexCoord2f(0.0, 1.0); glVertex2f(-1.0,  1.0)
    glEnd()

# Loop principal
while not glfw.window_should_close(window):
    # Captura frame
    ret, frame = cap.read()
    if not ret:
        break

    # (Opcional) Detecta marcadores e desenha na imagem
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    detector = cv2.aruco.ArucoDetector(aruco_dict, aruco_params)
    corners, ids, _ = detector.detectMarkers(gray)
    if ids is not None:
        cv2.aruco.drawDetectedMarkers(frame, corners, ids)

    # Carrega frame como textura
    load_texture_from_frame(frame)

    # Renderiza
    glClear(GL_COLOR_BUFFER_BIT)
    draw_quad()

    glfw.swap_buffers(window)
    glfw.poll_events()

    # Tecla ESC para sair
    if glfw.get_key(window, glfw.KEY_ESCAPE) == glfw.PRESS:
        glfw.set_window_should_close(window, True)

# Limpeza
cap.release()
glDeleteTextures([texture_id])
glfw.terminate()
