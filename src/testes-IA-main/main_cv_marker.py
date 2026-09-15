import glfw
import OpenGL.GL as gl
import glm
import cv2
import numpy as np
import math

from window import Window
from camera import Camera
from vision import Vision


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

    vision = Vision(camera_id=0)
    vision.open()

    tag_size = 0.05

    while not win.should_close():
        gl.glClear(gl.GL_DEPTH_BUFFER_BIT | gl.GL_COLOR_BUFFER_BIT)

        vision.update_camera_background(win.get_aspect_ratio())

        frame = vision.get_framebuffer()
        if frame is not None:
            vision.detect_markers()

            if 20 in vision.tag_IDs:
                idx = vision.tag_IDs.index(20)
                corners = vision.tags_corners[idx]

                half = tag_size / 2.0
                object_points = np.array([
                    [-half,  half, 0.0],
                    [half,  half, 0.0],
                    [half, -half, 0.0],
                    [-half, -half, 0.0]
                ], dtype=np.float32)

                fov_y_rad = math.radians(camera.get_zoom())
                fy = (frame.shape[0] / 2.0) / math.tan(fov_y_rad / 2.0)
                fx = fy
                cx = frame.shape[1] / 2.0
                cy = frame.shape[0] / 2.0

                camera_matrix = np.array([
                    [fx, 0.0, cx],
                    [0.0, fy, cy],
                    [0.0, 0.0, 1.0]
                ], dtype=np.float64)

                dist_coeffs = np.zeros((4, 1), dtype=np.float64)
                tag_corners_np = np.array(corners, dtype=np.float32)

                success, rvec, tvec = cv2.solvePnP(
                    object_points,
                    tag_corners_np,
                    camera_matrix,
                    dist_coeffs,
                    flags=cv2.SOLVEPNP_IPPE_SQUARE
                )

                if success:
                    x = float(tvec[0][0])
                    y = float(-tvec[1][0])
                    z = float(-tvec[2][0])
                    print(f"id=20  pos=({x:.4f}, {y:.4f}, {z:.4f})")

        win.swap_buffers()
        win.poll_events()

    vision.close()
    win.destroy()
    glfw.terminate()
    return 0


if __name__ == "__main__":
    main()
