# -*- coding: utf-8 -*-
import sys

import OpenGL.GL as gl
import OpenGL.GLUT as glut


class App(object):
    def __init__(
        self,
        width=512,
        height=512,
        fps=60,
        window_name='gl2dl rocks!',
        **kwargs
    ):
        self.width = width
        self.height = height

        glut.glutInit()
        glut.glutInitDisplayMode(
            # note: glut.GLUT_3_2_CORE_PROFILE is for Mac OS X
            glut.GLUT_DOUBLE | glut.GLUT_RGBA | glut.GLUT_3_2_CORE_PROFILE
        )
        glut.glutCreateWindow(window_name)
        glut.glutReshapeWindow(self.width, self.height)

        self.init(**kwargs)

        glut.glutReshapeFunc(self._reshape)
        glut.glutTimerFunc(1000/60, self._timer, fps)
        glut.glutDisplayFunc(self._display)

        glut.glutKeyboardFunc(self.keyboard)

        glut.glutMotionFunc(self.on_mouse_move)
        glut.glutPassiveMotionFunc(self.on_mouse_move)

    def init(self, **kwargs):
        """non-gl initialization handler stub"""

    def loop(self):
        glut.glutMainLoop()

    def _display(self):
        try:
            self.display()
        finally:
            gl.glBindVertexArray(0)
            gl.glUseProgram(0)

            gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)
            gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, 0)

            glut.glutSwapBuffers()

    def display(self):
        """User defined diplay handler stub"""

    def _reshape(self, width, height):
        gl.glViewport(0, 0, width, height)
        self.width = width
        self.height = height
        self.reshape(width, height)

    def reshape(self, width, height):
        """reshape handler stub"""

    def _timer(self, fps):
        glut.glutTimerFunc(1000/fps, self._timer, fps)
        self.timer(fps)
        glut.glutPostRedisplay()

    def timer(self, fps):
        """User-defined timer handler stub"""

    def keyboard(self, key, *args):
        """User-defined kearboard event handler stub"""
        if key == '\033':
            sys.exit()

    def on_mouse_move(self, x, y):
        """User-defined "on mouse move" handler stub"""

    def clear(self, color=(0, 0, 0, 0)):
        """Clear the windown buffer"""
        gl.glClearColor(*color)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)
