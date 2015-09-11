# -*- coding: utf-8 -*-
import OpenGL.GL as gl


class ShaderCompilationError(RuntimeError):
    """Raised when GLSL shader compilation error occurs"""


class ShaderProgram(object):
    VERTEX = gl.GL_VERTEX_SHADER
    FRAGMENT = gl.GL_FRAGMENT_SHADER
    GEOMETRY = gl.GL_GEOMETRY_SHADER

    def __init__(
        self, vertex_code, fragment_code, geometry_code=None
    ):
        self.vertex = self._create_shader(vertex_code, self.VERTEX)
        self.fragment = self._create_shader(fragment_code, self.FRAGMENT)

        if geometry_code:
            self.geometry = self._create_shader(geometry_code, self.GEOMETRY)
        else:
            self.geometry = None

        self.program = self._link_shader_program(
            self.vertex, self.fragment, self.geometry
        )

    @staticmethod
    def _create_shader(code, shader_type):
        shader = gl.glCreateShader(shader_type)
        gl.glShaderSource(shader, code)
        gl.glCompileShader(shader)

        if not gl.glGetShaderiv(shader, gl.GL_COMPILE_STATUS):
            raise ShaderCompilationError(gl.glGetShaderInfoLog(shader))

        return shader

    @staticmethod
    def _link_shader_program(*shaders):

        program = gl.glCreateProgram()

        for shader in shaders:
            if shader:
                gl.glAttachShader(program, shader)

        gl.glLinkProgram(program)

        if not gl.glGetProgramiv(program, gl.GL_LINK_STATUS):
            raise RuntimeError(gl.glGetProgramInfoLog(program))

        for shader in shaders:
            if shader:
                gl.glDetachShader(program, shader)

        return program
