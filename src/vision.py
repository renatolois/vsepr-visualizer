import cv2
import numpy as np
import glm
import math
import OpenGL.GL as gl

from shader import Shader
from transform import Transform
from camera import Camera


class Vision:
    def __init__(
        self,
        camera_id: int = 0,
        marker_type: int = cv2.aruco.DICT_APRILTAG_36H11
    ):
        self.camera_id = camera_id
        self.aruco_dict = cv2.aruco.getPredefinedDictionary(marker_type)
        self.aruco_params = cv2.aruco.DetectorParameters()
        self.aruco_params.markerBorderBits = 1

        self.stream = None
        self.framebuffer = None
        self.gray_frame = None
        self.tags_corners = []
        self.tag_ids = None

        self._bg_initialized = False
        self._bg_shader = None
        self._bg_texture_id = 0
        self._bg_vao = 0
        self._bg_vbo = 0
        self._bg_ebo = 0
        self._bg_identity = glm.mat4(1.0)

        self._frame_count = 0

    def open(self):
        if self.stream is not None and self.stream.isOpened():
            raise RuntimeError("camera already opened")

        self.stream = cv2.VideoCapture(self.camera_id, cv2.CAP_V4L2)
        if not self.stream.isOpened():
            self.stream.release()
            self.stream = None
            raise RuntimeError(
                f"failed to open camera with id {self.camera_id}")

        self.stream.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.stream.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.stream.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    def close(self):
        if self.stream is not None:
            self.stream.release()
            self.stream = None

    def read(self) -> bool:
        if self.stream is None:
            return False
        ok, frame = self.stream.read()
        if ok:
            self.framebuffer = frame
        return ok

    def get_framebuffer(self):
        return self.framebuffer

    def _bg_init(self):
        self._bg_shader = Shader(
            "src/shaders/vertex_shader_bg.glsl",
            "src/shaders/fragment_shader_bg.glsl",
        )

        self._bg_texture_id = gl.glGenTextures(1)
        gl.glBindTexture(gl.GL_TEXTURE_2D, self._bg_texture_id)
        gl.glTexParameteri(
            gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
        gl.glTexParameteri(
            gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)
        gl.glTexParameteri(
            gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP_TO_EDGE)
        gl.glTexParameteri(
            gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP_TO_EDGE)
        gl.glBindTexture(gl.GL_TEXTURE_2D, 0)

        vertices = np.array([
            -1.0,  1.0,  0.0,  0, 0, 1,  0.0, 1.0,
            1.0,  1.0,  0.0,  0, 0, 1,  1.0, 1.0,
            -1.0, -1.0,  0.0,  0, 0, 1,  0.0, 0.0,
            1.0, -1.0,  0.0,  0, 0, 1,  1.0, 0.0,
        ], dtype=np.float32)

        indices = np.array([0, 1, 2, 1, 2, 3], dtype=np.uint32)

        self._bg_vao = gl.glGenVertexArrays(1)
        self._bg_vbo = gl.glGenBuffers(1)
        self._bg_ebo = gl.glGenBuffers(1)

        gl.glBindVertexArray(self._bg_vao)

        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self._bg_vbo)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, vertices.nbytes,
                        vertices, gl.GL_STATIC_DRAW)

        gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, self._bg_ebo)
        gl.glBufferData(gl.GL_ELEMENT_ARRAY_BUFFER, indices.nbytes,
                        indices, gl.GL_STATIC_DRAW)

        stride = 8 * 4

        gl.glEnableVertexAttribArray(0)
        gl.glVertexAttribPointer(0, 3, gl.GL_FLOAT, gl.GL_FALSE, stride,
                                 gl.ctypes.c_void_p(0))
        gl.glEnableVertexAttribArray(1)
        gl.glVertexAttribPointer(1, 3, gl.GL_FLOAT, gl.GL_FALSE, stride,
                                 gl.ctypes.c_void_p(3 * 4))
        gl.glEnableVertexAttribArray(2)
        gl.glVertexAttribPointer(2, 2, gl.GL_FLOAT, gl.GL_FALSE, stride,
                                 gl.ctypes.c_void_p(6 * 4))

        gl.glBindVertexArray(0)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)
        gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, 0)

        self._bg_initialized = True

    def update_camera_background(self, aspect_ratio: float = 4.0 / 3.0):
        self.read()
        if self.framebuffer is None:
            return

        if not self._bg_initialized:
            self._bg_init()

        rgb = cv2.cvtColor(self.framebuffer, cv2.COLOR_BGR2RGB)
        rgb = np.flipud(rgb).copy()

        gl.glBindTexture(gl.GL_TEXTURE_2D, self._bg_texture_id)
        gl.glTexImage2D(
            gl.GL_TEXTURE_2D, 0, gl.GL_RGB,
            rgb.shape[1], rgb.shape[0], 0,
            gl.GL_RGB, gl.GL_UNSIGNED_BYTE, rgb
        )
        gl.glBindTexture(gl.GL_TEXTURE_2D, 0)

        gl.glDisable(gl.GL_DEPTH_TEST)

        self._bg_shader.use()

        self._bg_shader.set_uniform("material.transform", self._bg_identity)
        self._bg_shader.set_uniform("material.camera_view", self._bg_identity)
        self._bg_shader.set_uniform(
            "material.camera_projection", self._bg_identity)
        self._bg_shader.set_uniform("material.diffuse", 0)

        gl.glActiveTexture(gl.GL_TEXTURE0)
        gl.glBindTexture(gl.GL_TEXTURE_2D, self._bg_texture_id)

        gl.glBindVertexArray(self._bg_vao)
        gl.glDrawElements(gl.GL_TRIANGLES, 6, gl.GL_UNSIGNED_INT, None)
        gl.glBindVertexArray(0)

        gl.glEnable(gl.GL_DEPTH_TEST)

    def set_aruco_params(self, aruco_params: cv2.aruco.DetectorParameters) -> None:
        self.aruco_params = aruco_params

    def get_aruco_params(self) -> cv2.aruco.DetectorParameters:
        return self.aruco_params

    def detect_markers(self) -> bool:
        if self.framebuffer is None:
            self.tags_corners = []
            self.tag_IDs = []
            return False

        self.gray_frame = cv2.cvtColor(self.framebuffer, cv2.COLOR_BGR2GRAY)

        detector = cv2.aruco.ArucoDetector(
            self.aruco_dict,
            self.aruco_params
        )

        corners, ids, _ = detector.detectMarkers(self.gray_frame)

        self.tags_corners = corners if corners is not None else []
        self.tag_IDs = ids.flatten().tolist() if ids is not None else []

        return len(self.tag_IDs) > 0

    def get_marker_transform(
        self,
        tag_corners,
        camera: Camera,
        image_width: float,
        image_height: float,
        tag_size: float
    ) -> Transform:
        corners = np.array(tag_corners, dtype=np.float32).reshape(4, 2)
        if corners.shape[0] != 4:
            return Transform()

        half = tag_size / 2.0

        object_points = np.array([
            [-half,  half, 0.0],
            [ half,  half, 0.0],
            [ half, -half, 0.0],
            [-half, -half, 0.0]
        ], dtype=np.float32)

        fov_y_rad = math.radians(camera.get_zoom())
        fy = (image_height / 2.0) / math.tan(fov_y_rad / 2.0)
        fx = fy
        cx = image_width / 2.0
        cy = image_height / 2.0

        camera_matrix = np.array([
            [fx,  0.0, cx],
            [0.0, fy,  cy],
            [0.0, 0.0, 1.0]
        ], dtype=np.float64)

        dist_coeffs = np.zeros((4, 1), dtype=np.float64)

        success, rvec, tvec = cv2.solvePnP(
            object_points,
            corners,
            camera_matrix,
            dist_coeffs,
            flags=cv2.SOLVEPNP_IPPE_SQUARE
        )

        if not success:
            return Transform()

        rotation_matrix, _ = cv2.Rodrigues(rvec)

        # --- Posição: OpenCV (X, Y, Z) -> OpenGL (X, -Y, -Z) ---
        position = glm.vec3(
            float(tvec[0][0]),
            float(-tvec[1][0]),
            float(-tvec[2][0])
        )

        # --- Rotação: monta a matriz no formato glm ---
        glm_rot = glm.mat3(1.0)

        glm_rot[0][0] = float(rotation_matrix[0, 0])
        glm_rot[0][1] = -float(rotation_matrix[1, 0])
        glm_rot[0][2] = -float(rotation_matrix[2, 0])

        glm_rot[1][0] = -float(rotation_matrix[0, 1])
        glm_rot[1][1] = float(rotation_matrix[1, 1])
        glm_rot[1][2] = float(rotation_matrix[2, 1])

        glm_rot[2][0] = -float(rotation_matrix[0, 2])
        glm_rot[2][1] = float(rotation_matrix[1, 2])
        glm_rot[2][2] = float(rotation_matrix[2, 2])

        # --- Correção: rotação de 180° em Y (inverte X e Z locais) ---
        # Converte glm_rot -> numpy (transpondo, pois glm_rot[col][row])
        R_np = np.array([
            [glm_rot[0][0], glm_rot[1][0], glm_rot[2][0]],
            [glm_rot[0][1], glm_rot[1][1], glm_rot[2][1]],
            [glm_rot[0][2], glm_rot[1][2], glm_rot[2][2]],
        ], dtype=np.float64)

        R_y_180 = np.array([
            [-1.0, 0.0,  0.0],
            [ 0.0, 1.0,  0.0],
            [ 0.0, 0.0, -1.0]
        ], dtype=np.float64)

        R_final = R_np @ R_y_180

        # Converte de volta pra glm.mat3 (coluna x linha)
        glm_rot = glm.mat3(1.0)
        for col in range(3):
            for row in range(3):
                glm_rot[col][row] = float(R_final[row, col])

        rotation = glm.quat_cast(glm_rot)

        # -----------------------------------------------------------------
        # PRINTS DE DEBUG (a cada 30 frames)
        # -----------------------------------------------------------------
        self._frame_count += 1
        if self._frame_count % 30 == 0:
            # Extrai os eixos locais do marcador a partir da glm_rot FINAL
            x_axis = np.array([R_final[0, 0], R_final[1, 0], R_final[2, 0]])
            y_axis = np.array([R_final[0, 1], R_final[1, 1], R_final[2, 1]])
            z_axis = np.array([R_final[0, 2], R_final[1, 2], R_final[2, 2]])

            det = np.linalg.det(R_final)

        return Transform(position, rotation, glm.vec3(1.0, 1.0, 1.0))
