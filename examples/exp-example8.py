# -*- coding: utf-8 -*-
"""
This example shows that there is need to draw rects in batches!
"""
import random

import OpenGL.GLUT as glut
import OpenGL.GL as gl

from gl2dl.app import App
from gl2dl.lights import GLight
from gl2dl.primitives import BaseRect, RectBatch, rect_triangles
from gl2dl import blending
from gl2dl.sprites import Sprite


class FBTexture(object):
    def __init__(self, fb_tex):
        self.VAO = gl.glGenVertexArrays(1)
        gl.glBindVertexArray(self.VAO)

        self.texture = fb_tex
        self.uv_data = rect_triangles(0, 0, 1, 1)

        self.UVB = gl.glGenBuffers(1)

        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.UVB)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, self.uv_data.nbytes, self.uv_data, gl.GL_STATIC_READ)  # noqa
        # note: location of buffer?
        gl.glEnableVertexAttribArray(1)

    @property
    def width(self):
        return 512

    @property
    def height(self):
        return 512


class GLAPP(App):
    def init(self, size, positions):
        self.rect_batch = RectBatch()

        for pos in positions:
            self.rect_batch.append([pos, BaseRect(*size)])

        occluders = self.rect_batch.get_triangles()

        self.mouse_light = GLight((1, 0, 0), (1, 1,), occluders)
        self.static_lights = [
            GLight((0, 1, 0), (100, 100,), occluders),
            GLight((0, 0, 1), (400, 100,), occluders)
        ]

        self.fb = gl.glGenFramebuffers(1)
        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, self.fb)

        self.tx = gl.glGenTextures(1)
        gl.glBindTexture(gl.GL_TEXTURE_2D, self.tx)
        gl.glTexImage2D(
            gl.GL_TEXTURE_2D, 0, gl.GL_RGB,
            512, 512,
            0, gl.GL_RGB, gl.GL_UNSIGNED_BYTE, None
        )
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)
        gl.glFramebufferTexture2D(
            gl.GL_FRAMEBUFFER, gl.GL_COLOR_ATTACHMENT0, gl.GL_TEXTURE_2D, self.tx, 0
        )
        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, 0)


    def on_mouse_move(self, x, y):
        self.mouse_light.position = x, glut.glutGet(glut.GLUT_WINDOW_HEIGHT) - y

    def loop(self):
        super(GLAPP, self).loop()

    def display(self):
        self.sprite = Sprite(texture=FBTexture(self.tx))

        try:
            self.clear()

            gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, self.fb)
            self.mouse_light.draw()
            gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, 0)

            self.sprite.draw(0, 0, scale=1)

            for light in self.static_lights:
                gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, self.fb)
                light.draw()
                gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, 0)

                with blending.blending(mode=blending.Mode.MAX):
                    self.sprite.draw(0, 0, scale=1)

            self.rect_batch.draw()

        except Exception as err:
            print(err)
            exit(1)


if __name__ == '__main__':
    size = 10, 10

    positions = [
        (x * random.randint(80, 160), y * random.randint(80, 160))
        for x in range(5)
        for y in range(5)
    ]

    app = GLAPP(size=size, positions=positions)

    app.loop()

