# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
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

        glut.glutKeyboardFunc(self.keyboard)
        glut.glutDisplayFunc(self.display)

        glut.glutMotionFunc(self.on_mouse_move)
        glut.glutPassiveMotionFunc(self.on_mouse_move)

    def init(self, **kwargs):
        """non-gl initialization handler stub"""

    def loop(self):
        glut.glutMainLoop()

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
