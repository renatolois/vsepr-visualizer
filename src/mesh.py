import OpenGL.GL as gl
import numpy as np
import ctypes


class Mesh:
    def __init__(self, vertices, indices=None):
        if indices is None:
            indices = []
        self.vertices = vertices
        self.indices = indices
        self.VAO = 0
        self.VBO = 0
        self.EBO = 0
        self.setup_mesh()

    def destroy(self):
        if self.VAO:
            gl.glDeleteVertexArrays(1, [self.VAO])
        if self.VBO:
            gl.glDeleteBuffers(1, [self.VBO])
        if self.EBO:
            gl.glDeleteBuffers(1, [self.EBO])

    def get_indices_size(self):
        return len(self.indices)

    def setup_mesh(self):
        self.VAO = gl.glGenVertexArrays(1)
        self.VBO = gl.glGenBuffers(1)

        gl.glBindVertexArray(self.VAO)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.VBO)

        vertex_data = []
        for v in self.vertices:
            vertex_data.extend([v.position.x, v.position.y, v.position.z])
            vertex_data.extend([v.normal.x, v.normal.y, v.normal.z])
            vertex_data.extend([v.tex_coords.x, v.tex_coords.y])

        vertex_data_np = np.array(vertex_data, dtype=np.float32)

        gl.glBufferData(
            gl.GL_ARRAY_BUFFER,
            vertex_data_np.nbytes,
            vertex_data_np,
            gl.GL_STATIC_DRAW
        )

        if len(self.indices) != 0:
            indices_np = np.array(self.indices, dtype=np.uint32)
            self.EBO = gl.glGenBuffers(1)
            gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, self.EBO)
            gl.glBufferData(
                gl.GL_ELEMENT_ARRAY_BUFFER,
                indices_np.nbytes,
                indices_np,
                gl.GL_STATIC_DRAW
            )
        else:
            self.EBO = 0
            gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, 0)

        stride = 8 * 4  # (3 floats + 3 floats + 2 floats) * 4 bytes
        gl.glVertexAttribPointer(
            0,
            3,
            gl.GL_FLOAT,
            gl.GL_FALSE,
            stride,
            ctypes.c_void_p(0)
        )

        gl.glEnableVertexAttribArray(0)

        gl.glVertexAttribPointer(
            1,
            3,
            gl.GL_FLOAT,
            gl.GL_FALSE,
            stride,
            ctypes.c_void_p(12)
        )

        gl.glEnableVertexAttribArray(1)

        gl.glVertexAttribPointer(
            2,
            2,
            gl.GL_FLOAT,
            gl.GL_FALSE,
            stride,
            ctypes.c_void_p(24)
        )

        gl.glEnableVertexAttribArray(2)

        gl.glBindVertexArray(0)

    def bind(self):
        gl.glBindVertexArray(self.VAO)
