# -*- coding: utf-8 -*-


# -*- coding: utf-8 -*-
import atexit
import cProfile

import glfw
import OpenGL.GL as gl
import OpenGL.GLUT as glut


class GLFWApp(object):
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

        if not glfw.init():
            print("Could not initialize OpenGL context")
            self.exit()

        # Create a windowed mode window and its OpenGL context
        self.window = glfw.create_window(width, height, window_name, glfw.get_primary_monitor(), None)
        if not self.window:
            glfw.terminate()
            print("Could not initialize Window")
            self.exit()

        # Make the window's context current
        glfw.make_context_current(self.window)

        print("preinit")
        self.init()
        print("postinit")

    def init(self, **kwargs):
        """non-gl initialization handler stub"""

    def loop(self):
        # Loop until the user closes the window
        while not glfw.window_should_close(self.window):
            # Render here, e.g. using pyOpenGL
            print("predisplay")
            self._display()
            print("postdisplay")
            # Poll for and process events
            glfw.poll_events()

        glfw.terminate()


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

            glfw.swap_buffers(self.window)

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

    def _keyboard_up(self, key, *args):
        print(key, args)
        import sys; sys.stdout.flush()

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


import sys
from time import time

from gl2dl.app import App
from gl2dl.sprites import AnimatedSprite


class GLAPP(GLFWApp):
    def init(self):
        self.numbers = AnimatedSprite(
            # our spritesheet consists of 16x16 squares
            (16, 16),
            # and is implicely loaded from file
            'assets/numbers.png',
            # we set pivot in the centre of its dimensions
            pivot=(8, 8),
        )
        self.miner = AnimatedSprite(
            (64, 64),
            'assets/miner_animation.png',
            pivot=(32, 0)
        )

    def keyboard(self, key, *args):
        print ("keyboard: <%s> %s" % (key, args))
        sys.stdout.flush()

    def display(self):
        try:
            print("preclear")
            self.clear()
            print("postclear")
            # for the sake of simplicity we use time
            # as a source of frames
            self.numbers.draw(256, 256, scale=1, frame=time() * 3)
            print("postdraw2")
            self.miner.draw(256, 256 + 8, frame=time() * 10)
            print("postdraw")

        except Exception as err:
            print(err)
            exit(1)


if __name__ == '__main__':
    GLAPP().loop()
