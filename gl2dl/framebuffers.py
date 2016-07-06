# -*- coding: utf-8 -*-
from contextlib import contextmanager

import OpenGL.GL as gl

from gl2dl.primitives import rect_triangles
from gl2dl.sprites import Sprite


class FrameBufferTexture(object):
    """
    todo: very similar to Texture class, consider refactoring
    """
    def __init__(self, width, height):
        # todo: consider refactoring because it maybe can be moved somwhere
        # todo: else
        self.VAO = gl.glGenVertexArrays(1)
        gl.glBindVertexArray(self.VAO)

        self.width = width
        self.height = height

        # GL texture object initialization
        self.texture = gl.glGenTextures(1)
        gl.glBindTexture(gl.GL_TEXTURE_2D, self.texture)
        # note: we pass pixels=None because our texture is not initialized
        gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGB, width, height, 0, gl.GL_RGB, gl.GL_UNSIGNED_BYTE, None)  # noqa
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)  # noqa
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)  # noqa

        self.uv_data = rect_triangles(0, 0, 1, 1)
        self.UVB = gl.glGenBuffers(1)

        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.UVB)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, self.uv_data.nbytes, self.uv_data, gl.GL_STATIC_READ)  # noqa
        # note: location of buffer?
        gl.glEnableVertexAttribArray(1)

    def drawable(self):
        """ Return drawable object that can be rendered to buffer
        """
        return Sprite(texture=self)


class FrameBuffer(object):
    def __init__(self):
        self._framebuffer = gl.glGenFramebuffers(1)

    @contextmanager
    def to_texture(self, framebuffer_texture):

        # old_framebuffer = gl.glGetInteger(gl.GL_FRAMEBUFFER)
        old_framebuffer = 0
        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, self._framebuffer)
        gl.glFramebufferTexture2D(gl.GL_FRAMEBUFFER, gl.GL_COLOR_ATTACHMENT0, gl.GL_TEXTURE_2D, framebuffer_texture.texture, 0)

        try:
            yield
        finally:
            gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, old_framebuffer)

