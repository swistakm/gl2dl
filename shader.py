# -*- coding: utf-8 -*-
from functools import wraps

import OpenGL.GL as gl
import re


def _(fun):
    """
    Wrap matrix uniform function so it has exactly the same
    call arguments layout as other uniform (*v) functions
    """
    @wraps(fun)
    def wrapped_matrix_uniform(location, count, value):
        fun(location, count, True, value)

    return wrapped_matrix_uniform


class ShaderCompilationError(RuntimeError):
    """Raised when GLSL _shader compilation error occurs"""

    SHADER_ERR_RES = [
        re.compile(r'ERROR: (?P<file_num>\d+):(?P<line_num>\d+)'),
        re.compile(r'(?P<file_num>\d+)\((?P<line_num>\d+)\) : error'),
    ]

    def __init__(self, gl_msg, code):
        for re_ in self.SHADER_ERR_RES:
            match = re_.match(gl_msg)

            if match:
                file_num, line_num = (int(x) for x in match.groups())
                msg = "\n".join((
                    gl_msg,
                    '---------',
                    self._get_code_excerpt(code, line_num-1, '>>> '),
                    '---------',
                ))
                break
        else:
            msg = gl_msg

        super(ShaderCompilationError, self).__init__(msg)

    @staticmethod
    def _get_code_excerpt(code, line_num, padding):
        code_lines = code.split('\n')

        excerpt_lines = [
            " " * len(padding) + line for line in
            code_lines[max(0, line_num-2):line_num]
        ]

        line = code_lines[line_num]
        excerpt_lines.append(padding + line)

        return '\n'.join(excerpt_lines)

def unpack_ctypes(value):
    """ Convert ctypes arrays to normal python list if value is an ctypes
    array
    """
    # hack: this works because we know how ctypes array would behave
    #       in fact we do not care if this is really a ctypes array
    # todo: think about better approach
    return list(value) if hasattr(value, '__getitem__') else value


class ShaderProgram(object):
    """
    """

    VERTEX = gl.GL_VERTEX_SHADER
    FRAGMENT = gl.GL_FRAGMENT_SHADER
    GEOMETRY = gl.GL_GEOMETRY_SHADER

    TYPE_CONST_TO_SET_GET_TYPE = {

        gl.GL_BOOL:      (gl.glUniform1uiv, gl.glGetUniformuiv, gl.GLuint),
        gl.GL_BOOL_VEC2: (gl.glUniform2uiv, gl.glGetUniformuiv, gl.GLuint * 2),  # noqa
        gl.GL_BOOL_VEC3: (gl.glUniform3uiv, gl.glGetUniformuiv, gl.GLuint * 3),  # noqa
        gl.GL_BOOL_VEC4: (gl.glUniform4uiv, gl.glGetUniformuiv, gl.GLuint * 4),  # noqa

        gl.GL_UNSIGNED_INT:      (gl.glUniform1uiv, gl.glGetUniformuiv, gl.GLuint),  # noqa
        gl.GL_UNSIGNED_INT_VEC2: (gl.glUniform2uiv, gl.glGetUniformuiv, gl.GLuint * 2),  # noqa
        gl.GL_UNSIGNED_INT_VEC3: (gl.glUniform3uiv, gl.glGetUniformuiv, gl.GLuint * 3),  # noqa
        gl.GL_UNSIGNED_INT_VEC4: (gl.glUniform4uiv, gl.glGetUniformuiv, gl.GLuint * 4),  # noqa

        gl.GL_INT: (gl.glUniform1iv, gl.glGetUniformiv, gl.GLint),
        gl.GL_INT_VEC2: (gl.glUniform2iv, gl.glGetUniformiv, gl.GLint * 2),
        gl.GL_INT_VEC3: (gl.glUniform3iv, gl.glGetUniformiv, gl.GLint * 3),
        gl.GL_INT_VEC4: (gl.glUniform4iv, gl.glGetUniformiv, gl.GLint * 4),

        gl.GL_FLOAT: (gl.glUniform1fv, gl.glGetUniformfv, gl.GLfloat),
        gl.GL_FLOAT_VEC2: (gl.glUniform2fv, gl.glGetUniformfv, gl.GLfloat_2),
        gl.GL_FLOAT_VEC3: (gl.glUniform3fv, gl.glGetUniformfv, gl.GLfloat_3),
        gl.GL_FLOAT_VEC4: (gl.glUniform4fv, gl.glGetUniformfv, gl.GLfloat_4),

        gl.GL_FLOAT_MAT2: (_(gl.glUniformMatrix2fv), gl.glGetUniformfv, gl.GLfloat * 4),  # noqa
        gl.GL_FLOAT_MAT3: (_(gl.glUniformMatrix3fv), gl.glGetUniformfv, gl.GLfloat * 9),  # noqa
        gl.GL_FLOAT_MAT4: (_(gl.glUniformMatrix4fv), gl.glGetUniformfv, gl.GLfloat * 16),  # noqa

        gl.GL_FLOAT_MAT2x3: (_(gl.glUniformMatrix2x3fv), gl.glGetUniformfv, gl.GLfloat * 6),  # noqa
        gl.GL_FLOAT_MAT2x4: (_(gl.glUniformMatrix2x3fv), gl.glGetUniformfv, gl.GLfloat * 8),  # noqa

        gl.GL_FLOAT_MAT3x2: (_(gl.glUniformMatrix3x2fv), gl.glGetUniformfv, gl.GLfloat * 6),  # noqa
        gl.GL_FLOAT_MAT3x4: (_(gl.glUniformMatrix3x4fv), gl.glGetUniformfv, gl.GLfloat * 12),  # noqa

        gl.GL_FLOAT_MAT4x2: (_(gl.glUniformMatrix4x2fv), gl.glGetUniformfv, gl.GLfloat * 8),  # noqa
        gl.GL_FLOAT_MAT4x3: (_(gl.glUniformMatrix4x3fv), gl.glGetUniformfv, gl.GLfloat * 12),  # noqa

        gl.GL_SAMPLER_1D: (gl.glUniform1iv, gl.glGetUniformiv, gl.GLuint),
        gl.GL_SAMPLER_2D: (gl.glUniform1iv, gl.glGetUniformiv, gl.GLuint),
        gl.GL_SAMPLER_3D: (gl.glUniform1iv, gl.glGetUniformiv, gl.GLuint),
    }

    def __init__(
        self, vertex_code, fragment_code, geometry_code=None
    ):
        """
        TODO: way to ensure (at least with __debug__) that shader is bound when
            trying to set uniform
        :param vertex_code:
        :param fragment_code:
        :param geometry_code:
        :return:
        """
        self.vertex = self._create_shader(vertex_code, self.VERTEX)
        self.fragment = self._create_shader(fragment_code, self.FRAGMENT)

        if geometry_code:
            self.geometry = self._create_shader(geometry_code, self.GEOMETRY)
        else:
            self.geometry = None

        self.handle = self._link_shader_program(
            self.vertex, self.fragment, self.geometry
        )

        self._uniforms = self._prepare_uniforms()

    def __setitem__(self, key, value):
        if key in self._uniforms:
            size, gl_type = self._uniforms[key]

            location = gl.glGetUniformLocation(self.handle, key)
            setter, getter, __ = self.TYPE_CONST_TO_SET_GET_TYPE[gl_type]

            setter(location, size, value)

        else:
            raise KeyError("No active uniform of name: {}".format(key))

    def __getitem__(self, key):
        if key in self._uniforms:
            size, gl_type = self._uniforms[key]
            setter, getter, GLType = self.TYPE_CONST_TO_SET_GET_TYPE[gl_type]

            location = gl.glGetUniformLocation(self.handle, key)
            result = (GLType * size)()
            getter(self.handle, location, result)

            # Bacause we have same code/interface for dealing with arrays
            # and single-value uniforms do some unpacking so dynamically
            # typed minds won't be surprised
            return list(
                unpack_ctypes(elem) for elem in result
            ) if size > 1 else unpack_ctypes(result[0])

        else:
            raise KeyError("No active uniform of name: {}".format(key))

    def _prepare_uniforms(self):
        uniforms = {}

        nr_uniforms = gl.GLint()
        gl.glGetProgramiv(self.handle, gl.GL_ACTIVE_UNIFORMS, nr_uniforms)

        for uniform_index in xrange(nr_uniforms.value):
            name, size, gl_type = gl.glGetActiveUniform(
                self.handle,
                uniform_index,
            )
            # we know we are dealing with array and returned name will have
            # '[0]' at the end that we don't want to have in uniforms dict
            if size > 1 and '[0]' in name:
                name = name[:-3]

            uniforms[name] = size, gl_type

        return uniforms

    @staticmethod
    def _create_shader(code, shader_type):
        shader = gl.glCreateShader(shader_type)
        gl.glShaderSource(shader, code)
        gl.glCompileShader(shader)

        if not gl.glGetShaderiv(shader, gl.GL_COMPILE_STATUS):
            raise ShaderCompilationError(gl.glGetShaderInfoLog(shader), code)

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
        gl.glUseProgram(self.handle)

    @staticmethod
    def unbind():
        gl.glUseProgram(0)


