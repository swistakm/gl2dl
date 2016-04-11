# -*- coding: utf-8 -*-
from OpenGL import GL as gl
import OpenGL.GLUT as glut

import numpy as np

from .shaders import ShaderProgram


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


def ortho(width, height, x=0, y=0):
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


class Rect(BaseRect):
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

    def draw(self, x, y, color, scale=1.):
        with self._shader as active:
            active['model_view_projection'] = ortho(
                glut.glutGet(glut.GLUT_WINDOW_WIDTH),
                glut.glutGet(glut.GLUT_WINDOW_HEIGHT),
                x, y,
            )
            active['scale'] = scale
            active['color'] = color

            # draw rect triangles
            gl.glBindVertexArray(self.VAO)
            gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.VBO)
            gl.glVertexAttribPointer(0, 2, gl.GL_FLOAT, gl.GL_FALSE, 0, None)

            gl.glDrawArrays(gl.GL_TRIANGLES, 0, len(self._triangles))


class RectBatch(list):
    """ Special-case object for rendering multiple rectangles in single shader
    pass.

    FIXME: maybe deque will be better representation
    """

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

    def __init__(self, *args, **kwargs):
        super(RectBatch, self).__init__(*args, **kwargs)
        self._shader = ShaderProgram(self.vertex_code, self.fragment_code)
        self.VAO = gl.glGenVertexArrays(1)
        gl.glBindVertexArray(self.VAO)

        self.VBO = gl.glGenBuffers(1)
        gl.glEnableVertexAttribArray(0)


    def get_triangles(self):
        triangles = np.array([], dtype=np.float32)

        # fixme: profile this
        triangles = np.concatenate([
            rect._triangles + np.array(position, dtype=np.float32)
            for position, rect in self
        ])

        return triangles

    def draw(self):
        # fixme: quadratic time performance, improve
        triangles = self.get_triangles()

        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.VBO)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, triangles.nbytes, triangles, gl.GL_STATIC_DRAW)  # noqa

        gl.glBindVertexArray(self.VAO)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.VBO)
        gl.glVertexAttribPointer(0, 2, gl.GL_FLOAT, gl.GL_FALSE, 0, None)

        with self._shader as active:
            active['model_view_projection'] = ortho(
                glut.glutGet(glut.GLUT_WINDOW_WIDTH),
                glut.glutGet(glut.GLUT_WINDOW_HEIGHT),
                0, 0,
            )

            active['scale'] = 1.
            active['color'] = [1, 1, 1, 1]

            # draw rect triangles
            gl.glDrawArrays(gl.GL_TRIANGLES, 0, len(triangles))

