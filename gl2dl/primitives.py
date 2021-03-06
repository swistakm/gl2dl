# -*- coding: utf-8 -*-
import ctypes
from dataclasses import dataclass

from OpenGL import GL as gl
import numpy as np

from .shaders import ShaderProgram
from .app import window


def rect_triangles(x1, y1, x2, y2):
    return np.array([
        [x1, y1],
        [x1, y2],
        [x2, y2],
        # second triangle of sprite rect
        [x2, y1],
        [x2, y2],
        [x1, y1],
    ], dtype=np.float32)


def ortho(width, height, x=0, y=0, flip_x=False, flip_y=False):
    """
    Return orthographic projection matrix

    :param width: viewport width
    :param height: viewport heigth
    :param x: x position of object
    :param y: y position of object
    :return: 4x4 np.ndarray
    """
    matrix = np.array([
        [2./width, 0,         0,  -(2. * -x + width)/width],
        [0,        2./height, 0,  -(2. * -y + height)/height],
        [0,        0,         -2, -1],
        [0,        0,         0,  1.],
    ], dtype=np.float32)

    if flip_x:
        matrix[0, 0] *= -1

    if flip_y:
        matrix[1, 1] *= -1

    return matrix


class BaseRect(object):
    """ Base rectangle implementation that do not implement rendering.

    Used only for storing rectangle parameters and providing common API.
    """

    def __init__(self, width, height, pivot=(0, 0)):
        self.width = width
        self.height = height
        self.pivot = pivot

        self._triangles = rect_triangles(
            0, 0, width, height
        ) - np.array(pivot, dtype=np.float32)

    @classmethod
    def sized(cls, x, y, width, height):
        return cls(x, y, x + width, y + height)


@dataclass
class Vec1:
    x: float


@dataclass
class Vec2:
    x: float
    y: float


@dataclass
class Vec3:
    x: float
    y: float
    z: float


@dataclass
class Vec4:
    x: float
    y: float
    z: float
    w: float


class Triangles:
    vertex_code = """
    #version 330 core

    // Input vertex data, different for all executions of this shader.
    layout(location = 0) in vec2 position;
    layout(location = 1) in vec4 color;

    uniform mat4 model_view_projection;
    uniform float scale;

    out vec4 v_color;

    void main(){
        gl_Position =  model_view_projection * vec4(position, 0, 1/scale);
        v_color = color;
    }
    """

    fragment_code = """
        #version 330 core

        in vec4 v_color;
        out lowp vec4 out_color;

        void main(){
            out_color = v_color;
        }
    """

    def __init__(self, data: np.array, fb_scale: float = 1.):
        self._shader = ShaderProgram(self.vertex_code, self.fragment_code)
        self._fb_scale = fb_scale

        self.vao = gl.glGenVertexArrays(1)
        gl.glBindVertexArray(self.vao)

        self.vbo = gl.glGenBuffers(1)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.vbo)

        # set position
        gl.glEnableVertexAttribArray(0)
        gl.glVertexAttribPointer(0, 2, gl.GL_FLOAT, gl.GL_FALSE, 24, ctypes.c_void_p(0))
        # set color
        gl.glEnableVertexAttribArray(1)
        gl.glVertexAttribPointer(1, 4, gl.GL_FLOAT, gl.GL_FALSE, 24, ctypes.c_void_p(8))

        # unbind vbo
        gl.glBindVertexArray(0)
        self.data = data

    @property
    def data(self):
        return np.copy(self._data)

    @data.setter
    def data(self, value):
        self._data = value
        if len(self.data):
            gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.vbo)
            gl.glBufferData(gl.GL_ARRAY_BUFFER, self._data.nbytes, self._data, gl.GL_STATIC_DRAW)  # noqa

    def draw(self, scale=1.):
        with self._shader as active:
            active['scale'] = scale
            active['model_view_projection'] = ortho(
                window.width * self._fb_scale,
                window.height * self._fb_scale,
                0, 0,
            )
            gl.glBindVertexArray(self.vao)
            gl.glDrawArrays(gl.GL_TRIANGLES, 0, len(self._data))


class Rect(BaseRect):
    # todo: convert to traingle base
    vertex_code = """
        #version 330 core

        // Input vertex data, different for all executions of this shader.
        layout(location = 0) in vec2 vertexPosition;

        uniform mat4 model_view_projection;
        uniform float scale;

        void main(){
            gl_Position =  model_view_projection * vec4(vertexPosition, 0, 1/scale);
        }
    """

    fragment_code = """
        #version 330 core
        uniform vec4 color;

        in vec2 vertex_position;

        out lowp vec4 out_color;

        void main(){
            out_color = color;
        }
    """

    def __init__(self, width, height, pivot=(0, 0)):
        super(Rect, self).__init__(width, height, pivot)

        self._shader = ShaderProgram(self.vertex_code, self.fragment_code)

        self.width = width
        self.height = height

        self._triangles = rect_triangles(
            0, 0, width, height
        ) - np.array(pivot, dtype=np.float32)

        self.VAO = gl.glGenVertexArrays(1)
        gl.glBindVertexArray(self.VAO)

        self.VBO = gl.glGenBuffers(1)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.VBO)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, self._triangles.nbytes, self._triangles, gl.GL_STATIC_DRAW)  # noqa
        gl.glEnableVertexAttribArray(0)

        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.VBO)
        gl.glVertexAttribPointer(0, 2, gl.GL_FLOAT, gl.GL_FALSE, 0, None)

        # unbind VBO
        gl.glBindVertexArray(0)

    def draw(self, x, y, color, scale=1.):
        with self._shader as active:
            active['model_view_projection'] = ortho(
                window.width,
                window.height,
                x, y,
            )
            active['scale'] = scale
            active['color'] = color

            # draw rect triangles
            gl.glBindVertexArray(self.VAO)
            gl.glDrawArrays(gl.GL_TRIANGLES, 0, len(self._triangles))


class RectBatch(list):
    """ Special-case object for rendering multiple rectangles in single shader
    pass.

    FIXME: maybe deque will be better representation
    """
    # reuse shader code from rect as it is completely the same
    vertex_code = Rect.vertex_code
    fragment_code = Rect.fragment_code

    def __init__(self, *args, **kwargs):
        super(RectBatch, self).__init__(*args, **kwargs)
        self._shader = ShaderProgram(self.vertex_code, self.fragment_code)
        self.VAO = gl.glGenVertexArrays(1)
        gl.glBindVertexArray(self.VAO)

        self.VBO = gl.glGenBuffers(1)
        gl.glEnableVertexAttribArray(0)

    def get_triangles(self):
        # fixme: profile this
        triangles = np.concatenate([
            rect._triangles + np.array(position, dtype=np.float32)
            for position, rect in self
        ])

        return triangles

    def draw(self, color=None):
        # fixme: quadratic time performance, improve
        triangles = self.get_triangles()

        # fixme: no need to send buffer data every time batch is drawn
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.VBO)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, triangles.nbytes, triangles, gl.GL_STATIC_DRAW)  # noqa

        gl.glBindVertexArray(self.VAO)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.VBO)
        gl.glVertexAttribPointer(0, 2, gl.GL_FLOAT, gl.GL_FALSE, 0, None)

        with self._shader as active:
            active['model_view_projection'] = ortho(
                window.width,
                window.height,
                0, 0,
            )

            active['scale'] = 1.
            active['color'] = color or [1, 1, 1, 1]

            # draw rect triangles
            gl.glDrawArrays(gl.GL_TRIANGLES, 0, len(triangles))
