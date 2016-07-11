# -*- coding: utf-8 -*-
import atexit
import cProfile
import sys

import OpenGL.GL as gl
import OpenGL.GLUT as glut


class App(object):
    ENABLE_DEFAULT_KEYBOARD_HOOKS = True

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
        glut.glutTimerFunc(int(1000/60), self._timer, fps)
        glut.glutDisplayFunc(self._display)

        glut.glutKeyboardFunc(self._keyboard)
        glut.glutSpecialFunc(self._keyboard)

        glut.glutMotionFunc(self.on_mouse_move)
        glut.glutPassiveMotionFunc(self.on_mouse_move)

    def init(self, **kwargs):
        """non-gl initialization handler stub"""

    def loop(self):
        glut.glutMainLoop()

    def exit(self):
        sys.exit(0)

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
        glut.glutTimerFunc(int(1000/fps), self._timer, fps)
        self.timer(fps)
        glut.glutPostRedisplay()

    def timer(self, fps):
        """User-defined timer handler stub"""

    def _keyboard(self, key, *args):
        if self.ENABLE_DEFAULT_KEYBOARD_HOOKS:
            if key == b'\033':
                self.exit()

        self.keyboard(key, *args)

    def keyboard(self, key, *args):
        """User-defined kearboard event handler stub"""

    def on_mouse_move(self, x, y):
        """User-defined "on mouse move" handler stub"""

    def clear(self, color=(0, 0, 0, 0)):
        """Clear the windown buffer"""
        gl.glClearColor(*color)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)

    def enable_profiling(self, filename=None):
        """ Enable profiling session for application.

        Profiler will quit on process exit. This is workaround for not being
        able to controll event loop in GLUT.

        :param filename: filename to save profiler stats to. If it is set to
            None then stats are printed on stdout instead. Defaults to None
        """
        def quit_profiler_at_exit(profiler):
            profiler.disable()

            if filename:
                profiler.dump_stats(filename)
            else:
                profiler.print_stats()

        profiler = cProfile.Profile()
        atexit.register(quit_profiler_at_exit, profiler)
        profiler.enable()
