# -*- coding: utf-8 -*-
import OpenGL.GL as gl


class ShaderCompilationError(RuntimeError):
    """Raised when GLSL shader compilation error occurs"""


class ShaderProgram(object):
    """
    Todo:
    * rename .program to .handle
    * write bind/unbind methods

    """

    VERTEX = gl.GL_VERTEX_SHADER
    FRAGMENT = gl.GL_FRAGMENT_SHADER
    GEOMETRY = gl.GL_GEOMETRY_SHADER

    UNIFORM_TYPES = {
        gl.GL_FLOAT: (gl.glProgramUniform1f, gl.glGetUniformfv),
        gl.GL_FLOAT_VEC3: (gl.glProgramUniform3f, gl.glGetUniformfv)
    }

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

        self._uniforms = self._prepare_uniforms()

    def __setitem__(self, key, value):
        if key in self._uniforms:
            size, gl_type = self._uniforms[key]

            location = gl.glGetUniformLocation(self.program, key)
            setter, getter = self.UNIFORM_TYPES[gl_type]

            if isinstance(value, (list, tuple)):
                setter(self.program, location, *value)
            else:
                setter(self.program, location, value)

        else:
            KeyError("No active uniform of name: {}".format(key))

    def __getitem__(self, key):
        if key in self._uniforms:
            size, gl_type = self._uniforms[key]

            location = gl.glGetUniformLocation(self.program, key)
            setter, getter = self.UNIFORM_TYPES[gl_type]
            # todo: introspect type
            value = (gl.GLfloat * size)()
            getter(self.program, location, value)
            return list(value)

        else:
            KeyError("No active uniform of name: {}".format(key))

    def _prepare_uniforms(self):
        uniforms = {}

        nr_uniforms = gl.GLint()
        gl.glGetProgramiv(self.program, gl.GL_ACTIVE_UNIFORMS, nr_uniforms)

        for uniform_index in xrange(nr_uniforms.value):
            name, size, gl_type = gl.glGetActiveUniform(
                self.program,
                uniform_index,
            )
            uniforms[name] = size, gl_type

        print uniforms
        return uniforms


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

    def bind(self):
        gl.glUseProgram(self.program)

    @staticmethod
    def unbind():
        gl.glUseProgram(0)


