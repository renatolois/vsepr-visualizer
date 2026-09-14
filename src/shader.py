import OpenGL.GL as gl
import glm
import sys


def _read_shader(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            content = file.read()
            return content
    except FileNotFoundError:
        print("failed to open shader file", file=sys.stderr)
        return None
    except Exception:
        print("failed to open shader file", file=sys.stderr)
        return None


class Shader:
    def __init__(self, vtxShaderFilepath, frgShaderFilepath):
        vtxShaderFileBuffer = _read_shader(vtxShaderFilepath)
        if vtxShaderFileBuffer is None:
            error = vtxShaderFilepath + "\nfailed to open vertex shader file"
            raise RuntimeError(error)

        frgShaderFileBuffer = _read_shader(frgShaderFilepath)
        if frgShaderFileBuffer is None:
            error = frgShaderFilepath + "\nfailed to open fragment shader file"
            raise RuntimeError(error)

        vtxShaderId = gl.glCreateShader(gl.GL_VERTEX_SHADER)
        frgShaderId = gl.glCreateShader(gl.GL_FRAGMENT_SHADER)

        gl.glShaderSource(vtxShaderId, vtxShaderFileBuffer)
        gl.glShaderSource(frgShaderId, frgShaderFileBuffer)

        gl.glCompileShader(vtxShaderId)
        gl.glCompileShader(frgShaderId)

        compileSuccess = gl.glGetShaderiv(vtxShaderId, gl.GL_COMPILE_STATUS)
        if compileSuccess == gl.GL_FALSE:
            logBuffer = gl.glGetShaderInfoLog(vtxShaderId)
            gl.glDeleteShader(vtxShaderId)
            gl.glDeleteShader(frgShaderId)
            error = vtxShaderFilepath + ":\n" + logBuffer.decode('utf-8')
            raise RuntimeError(error)

        compileSuccess = gl.glGetShaderiv(frgShaderId, gl.GL_COMPILE_STATUS)
        if compileSuccess == gl.GL_FALSE:
            logBuffer = gl.glGetShaderInfoLog(frgShaderId)
            gl.glDeleteShader(vtxShaderId)
            gl.glDeleteShader(frgShaderId)

            error = frgShaderFilepath + ":\n" + logBuffer.decode('utf-8')
            raise RuntimeError(error)

        self.program_id = gl.glCreateProgram()
        gl.glAttachShader(self.program_id, vtxShaderId)
        gl.glAttachShader(self.program_id, frgShaderId)
        gl.glLinkProgram(self.program_id)
        gl.glDetachShader(self.program_id, vtxShaderId)
        gl.glDetachShader(self.program_id, frgShaderId)

        linkSuccess = gl.glGetProgramiv(self.program_id, gl.GL_LINK_STATUS)
        if linkSuccess == gl.GL_FALSE:
            logBuffer = gl.glGetProgramInfoLog(self.program_id)
            gl.glDeleteShader(vtxShaderId)
            gl.glDeleteShader(frgShaderId)
            gl.glDeleteProgram(self.program_id)
            error = "Program Link Error: \n" + logBuffer.decode('utf-8')
            raise RuntimeError(error)

        gl.glDeleteShader(vtxShaderId)
        gl.glDeleteShader(frgShaderId)

    def destroy(self):
        if hasattr(self, 'program_id'):
            gl.glDeleteProgram(self.program_id)

    def set_uniform(self, uniform_name, value):
        location = gl.glGetUniformLocation(self.program_id, uniform_name)
        if location == -1:
            print(
                f"Warning: uniform '{uniform_name}' not found in program with id = {self.program_id}",  # noqa: E501
                file=sys.stderr
            )
            return

        if isinstance(value, int):
            gl.glUniform1i(location, value)
        elif isinstance(value, float):
            gl.glUniform1f(location, value)
        elif isinstance(value, glm.mat4):
            gl.glUniformMatrix4fv(
                location,
                1,
                gl.GL_FALSE,
                glm.value_ptr(value)
            )
        elif isinstance(value, glm.vec3):
            gl.glUniform3fv(location, 1, glm.value_ptr(value))
        elif isinstance(value, glm.vec4):
            gl.glUniform4fv(location, 1, glm.value_ptr(value))
        else:
            raise TypeError(f"Unsupported type for uniform: {type(value)}")

    def use(self):
        gl.glUseProgram(self.program_id)
