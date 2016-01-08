# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
import sys

import OpenGL.GL as gl
import OpenGL.GLUT as glut

from PIL import Image
import numpy as np

from shaders import ShaderProgram
from sprites import Sprite


class GLAPP(object):
    def __init__(self, data):
        self.width = 512
        self.height = 512
        glut.glutInit()
        glut.glutInitDisplayMode(
            # note: glut.GLUT_3_2_CORE_PROFILE is for Mac OS X
            glut.GLUT_DOUBLE | glut.GLUT_RGBA | glut.GLUT_3_2_CORE_PROFILE
        )
        glut.glutCreateWindow('Hello world!')
        glut.glutReshapeWindow(self.width, self.height)

        self.data = data

        glut.glutReshapeFunc(self.reshape)
        glut.glutKeyboardFunc(self.keyboard)
        glut.glutDisplayFunc(self.display)

        glut.glutTimerFunc(1000/60, self.timer, 60)
        glut.glutMotionFunc(self.on_mouse_move)
        glut.glutPassiveMotionFunc(self.on_mouse_move)

        self.sprite = Sprite('marble.bmp')

    def on_mouse_move(self, x, y):
        pass

    def timer(self, fps):
        glut.glutTimerFunc(1000/fps, self.timer, fps)
        glut.glutPostRedisplay()

    def loop(self):
        glut.glutMainLoop()

    def display(self):
        # clear the buffer
        gl.glClearColor(0, 0, 0, 0)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)

        try:
            gl.glClearColor(0, 0, 0, 0)
            gl.glClear(gl.GL_COLOR_BUFFER_BIT)

            self.sprite.draw()

        except Exception as err:
            print err
            exit(1)

        finally:
            gl.glBindVertexArray(0)
            gl.glUseProgram(0)

            gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)
            gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, 0)

            glut.glutSwapBuffers()

    def reshape(self, width, height):
        gl.glViewport(0, 0, width, height)
        self.width = width
        self.height = height

    @staticmethod
    def keyboard(key, *args):
        if key == '\033':
            sys.exit()


if __name__ == '__main__':
    data = np.array([
        [-1, -1],
        [-1, 1],
        [1, 1],

        [1, -1],
        [1, 1],
        [-1, -1],
    ], dtype=np.float32) / 1.5

    GLAPP(data).loop()
