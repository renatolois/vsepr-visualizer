import cv2
import numpy as np
import math
from typing import List

from camera import Camera
from transform import Transform
from renderer import Renderer
from vertex import Vertex
from shader import Shader
from mesh import Mesh
from model import Model
from material import Material


class Vision:
    def __init__(
            self,
            cameraID: int,
            marker_type: int = cv2.aruco.DICT_6X6_250
    ):
        self.cameraID = cameraID
        self.aruco_dict = cv2.aruco.getPredefinedDictionary(marker_type)
        self.aruco_params = cv2.aruco.DetectorParameters()
        self.aruco_params.markerBorderBits = 1

        self.stream = None
        self.framebuffer = None
        self.gray_frame = None
        self.tags_corners = []
        self.tag_IDs = []

    def set_aruco_params(self, aruco_params: cv2.aruco.DetectorParameters):
        self.aruco_params = aruco_params

    def get_aruco_params(self) -> cv2.aruco.DetectorParameters:
        return self.aruco_params

    def open(self):
        if self.stream is not None and self.stream.isOpened():
            raise RuntimeError("camera already opened")
        self.stream = cv2.VideoCapture(self.cameraID, cv2.CAP_V4L2)
        if not self.stream.isOpened():
            self.stream.release()
            raise RuntimeError(
                f"failed to open camera with id {self.cameraID}"
            )
        self.stream.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.stream.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.stream.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    def close(self):
        if self.stream is not None:
            self.stream.release()
            self.stream = None

    def read(self) -> bool:
        if self.stream is None or not self.stream.isOpened():
            return False
        ret, frame = self.stream.read()
        if ret:
            self.framebuffer = frame
        return ret

    def get_framebuffer(self):
        return self.framebuffer

    def detect_markers(self) -> bool:
        if self.framebuffer is None:
            self.tags_corners = []
            self.tag_IDs = []
            return False
        self.gray_frame = cv2.cvtColor(self.framebuffer, cv2.COLOR_BGR2GRAY)
        detector = cv2.aruco.ArucoDetector(self.aruco_dict, self.aruco_params)

        corners, ids, _ = (
                detector.detectMarkers(self.gray_frame)
        )

        self.tags_corners = (
                corners if corners is not None else []
        )
        self.tag_IDs = ids.flatten().tolist() if ids is not None else []

        return self.tag_IDs is not None and len(self.tag_IDs) > 0

    def get_marker_transform(
        self,
        tag_corners: List[np.ndarray],
        camera: Camera,
        image_width: float,
        image_height: float,
        tag_size: float
    ) -> Transform:
        if len(tag_corners) != 4:
            return Transform()

        half = tag_size / 2.0
        object_points = np.array([
            [-half,  half, 0.0],
            [half,  half, 0.0],
            [half, -half, 0.0],
            [-half, -half, 0.0]
        ], dtype=np.float32)

        fov_y_rad = math.radians(camera.get_zoom())
        fy = (image_height / 2.0) / math.tan(fov_y_rad / 2.0)
        fx = fy
        cx = image_width / 2.0
        cy = image_height / 2.0

        camera_matrix = np.array([
            [fx, 0.0, cx],
            [0.0, fy, cy],
            [0.0, 0.0, 1.0]
        ], dtype=np.float64)

        dist_coeffs = np.zeros((4, 1), dtype=np.float64)
        tag_corners_np = np.array(tag_corners, dtype=np.float32)

        success, rvec, tvec = cv2.solvePnP(
            object_points,
            tag_corners_np,
            camera_matrix,
            dist_coeffs,
            flags=cv2.SOLVEPNP_IPPE
        )

        if not success:
            return Transform()

        R, _ = cv2.Rodrigues(rvec)

        position = np.array([
            tvec[0][0],
            -tvec[1][0],
            -tvec[2][0]
        ], dtype=np.float32)

        R_opengl = R.copy()
        R_opengl[1, :] = -R_opengl[1, :]
        R_opengl[2, :] = -R_opengl[2, :]

        def rotation_matrix_to_quaternion(R):
            trace = np.trace(R)
            if trace > 0:
                s = 0.5 / np.sqrt(trace + 1.0)
                w = 0.25 / s
                x = (R[2, 1] - R[1, 2]) * s
                y = (R[0, 2] - R[2, 0]) * s
                z = (R[1, 0] - R[0, 1]) * s
            else:
                if R[0, 0] > R[1, 1] and R[0, 0] > R[2, 2]:
                    s = 2.0 * np.sqrt(1.0 + R[0, 0] - R[1, 1] - R[2, 2])
                    w = (R[2, 1] - R[1, 2]) / s
                    x = 0.25 * s
                    y = (R[0, 1] + R[1, 0]) / s
                    z = (R[0, 2] + R[2, 0]) / s
                elif R[1, 1] > R[2, 2]:
                    s = 2.0 * np.sqrt(1.0 + R[1, 1] - R[0, 0] - R[2, 2])
                    w = (R[0, 2] - R[2, 0]) / s
                    x = (R[0, 1] + R[1, 0]) / s
                    y = 0.25 * s
                    z = (R[1, 2] + R[2, 1]) / s
                else:
                    s = 2.0 * np.sqrt(1.0 + R[2, 2] - R[0, 0] - R[1, 1])
                    w = (R[1, 0] - R[0, 1]) / s
                    x = (R[0, 2] + R[2, 0]) / s
                    y = (R[1, 2] + R[2, 1]) / s
                    z = 0.25 * s
            return np.array([x, y, z, w], dtype=np.float32)

        quat = rotation_matrix_to_quaternion(R_opengl)
        return Transform(position, quat, np.array([1.0, 1.0, 1.0]))

    def update_camera_background(self, aspect_ratio: float):
        if not hasattr(self, '_bg_initialized'):
            self._bg_initialized = False
            self._bg_camera = Camera()
            self._bg_renderer = Renderer()

            self._corner_vertices = [
                Vertex(
                    np.array([-1.0,  1.0, 0.0]),
                    np.array([0.0, 0.0, 0.0]),
                    np.array([0.0, 0.0])
                ),
                Vertex(
                    np.array([1.0,  1.0, 0.0]),
                    np.array([0.0, 0.0, 0.0]),
                    np.array([1.0, 0.0])
                ),
                Vertex(
                    np.array([-1.0, -1.0, 0.0]),
                    np.array([0.0, 0.0, 0.0]),
                    np.array([0.0, 1.0])
                ),
                Vertex(
                    np.array([1.0, -1.0, 0.0]),
                    np.array([0.0, 0.0, 0.0]),
                    np.array([1.0, 1.0])
                ),
            ]
            self._corner_indices = [0, 1, 2, 1, 2, 3]

            self._bg_mesh = Mesh(self._corner_vertices, self._corner_indices)
            self._bg_shader = Shader("res/shaders/vertex_shader_bg.glsl",
                                     "res/shaders/fragment_shader_bg.glsl")
            self._bg_material = Material(self._bg_shader)
            if hasattr(self._bg_material, 'set_use_texture'):
                self._bg_material.set_use_texture(False)

            self._bg_transform = Transform(
                np.array([0.0, 0.0, 0.0]),
                np.array([0.0, 0.0, 0.0, 1.0]),
                np.array([1.0, 1.0, 1.0])
            )

            self._bg_model = Model(
                [self._bg_mesh], [self._bg_material], [self._bg_transform]
            )

            self._bg_camera.set_aspect(aspect_ratio)

        self.read()

        if self.framebuffer is not None:
            cv2.imshow("Camera Feed", self.framebuffer)
            cv2.waitKey(1)

        if not self._bg_initialized:
            self._bg_initialized = True
