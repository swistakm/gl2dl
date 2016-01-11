# -*- coding: utf-8 -*-
import time
import math

import OpenGL.GL as gl
import OpenGL.GLUT as glut

import numpy as np

from app import App
from sprites import Sprite


class GLAPP(App):
    def init(self, data=None):
        self.data = data
        self.sprite = Sprite('marble.bmp')

    def display(self):
        try:
            # clear the buffer
            gl.glClearColor(0, 0, 0, 0)
            gl.glClear(gl.GL_COLOR_BUFFER_BIT)

            self.sprite.draw(scale=math.sin(time.time()))

        except Exception as err:
            print err
            exit(1)

        finally:
            gl.glBindVertexArray(0)
            gl.glUseProgram(0)

            gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)
            gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, 0)

            glut.glutSwapBuffers()


if __name__ == '__main__':
    data = np.array([
        [-1, -1],
        [-1, 1],
        [1, 1],

        [1, -1],
        [1, 1],
        [-1, -1],
    ], dtype=np.float32) / 1.5

    GLAPP(data=data).loop()
