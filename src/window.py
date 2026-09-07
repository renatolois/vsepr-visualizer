import sys
import glfw
import OpenGL.GL as gl


class Window:
    def __init__(self, width: int, height: int, title: str):
        self.width = width
        self.height = height
        self.title = title
        self.aspect_ratio = float(width) / float(height)

        self.window = None
        self.last_time = 0.0
        self.current_time = 0.0

    @staticmethod
    def _window_resize_callback(window, width: int, height: int):
        win = glfw.get_window_user_pointer(window)
        if win is None:
            return

        aspect_ratio = win.get_aspect_ratio()

        viewport_width = width
        viewport_height = height

        if width > (height * aspect_ratio):
            viewport_width = int(height * aspect_ratio)
        else:
            viewport_height = int(width / aspect_ratio)

        gl.glViewport(
            int((width / 2) - (viewport_width / 2)),
            int((height / 2) - (viewport_height / 2)),
            viewport_width,
            viewport_height
        )

    def get_width(self) -> int:
        return self.width

    def get_height(self) -> int:
        return self.height

    def init_backend(self) -> int:
        if not glfw.init():
            print("failed to initialize GLFW.", file=sys.stderr)
            return 1
        return 0

    def init(self) -> int:
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
        glfw.window_hint(glfw.VISIBLE, glfw.FALSE)
        glfw.window_hint(glfw.SAMPLES, 1)

        self.window = glfw.create_window(
            self.width,
            self.height,
            self.title,
            None,
            None
        )

        if not self.window:
            glfw.terminate()
            print("failed to create window.", file=sys.stderr)
            return 1

        glfw.set_window_user_pointer(self.window, self)

        glfw.make_context_current(self.window)

        glfw.set_framebuffer_size_callback(
            self.window,
            Window._window_resize_callback
        )

        return 0

    def destroy(self) -> int:
        if self.window:
            glfw.destroy_window(self.window)
            self.window = None
        return 0

    def is_visible(self) -> bool:
        return glfw.get_window_attrib(self.window, glfw.VISIBLE) == glfw.TRUE

    def set_visible(self, visible: bool):
        if visible:
            glfw.show_window(self.window)
        else:
            glfw.hide_window(self.window)

    def poll_events(self):
        glfw.poll_events()

    def swap_buffers(self):
        glfw.swap_buffers(self.window)

    def get_window(self):
        return self.window

    def get_current_time(self) -> float:
        return glfw.get_time()

    def get_delta_time(self) -> float:
        self.current_time = self.get_current_time()
        delta_time = self.current_time - self.last_time
        self.last_time = self.current_time
        return delta_time

    def should_close(self) -> bool:
        return glfw.window_should_close(self.window)

    def get_aspect_ratio(self) -> float:
        return self.aspect_ratio

    def set_aspect_ratio(self, aspect_ratio: float):
        self.aspect_ratio = aspect_ratio
