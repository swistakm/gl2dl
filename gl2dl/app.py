# -*- coding: utf-8 -*-
import atexit
import cProfile
import sys

import OpenGL.GL as gl
import OpenGL.GLUT as glut
import glfw

from . import compat


class WindowState(object):
    """ Semi-global window state for accessing GL context variables

    This is bit hacky solution that because we would like to have pluggable
    windowing toolkit like GLUT, GLFW etc. Use with care.

    todo: explain why context to window state may be attached only once
    todo: make it immutable or semi-immutable
    todo: try to find a way to prevent this module level object from
          any change (maybe some import hook magic)
    """
    def __init__(self):
        self._attached_context = None

    def attach_context(self, context):
        if self._attached_context:
            raise InitializationError(
                "Trying to initialize window when one already initialized"
            )
        self._attached_context = context

    @property
    def width(self):
        return self._attached_context.width

    @property
    def height(self):
        return self._attached_context.height

window = WindowState()


class InitializationError(RuntimeError):
    """ Raised when initialization error occured
    """


class BaseApp(object):
    ENABLE_DEFAULT_KEYBOARD_HOOKS = True

    def __init__(self, **kwargs):
        self.init(**kwargs)

    def init(self, **kwargs):
        """non-window initialization handler stub"""

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

    def clear(self, color=(0, 0, 0, 0)):
        """Clear the windown buffer"""
        gl.glClearColor(*color)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)

    def on_key(self, key, *args):
        """User-defined kearboard event handler stub"""

    def on_mouse_move(self, x, y):
        """User-defined "on mouse move" handler stub"""

    def on_resize(self, width, height):
        """reshape handler stub"""

    def on_exit(self):
        sys.exit(0)


class GlutApp(BaseApp):
    class GlutWindowContext(object):
        @property
        def width(self):
            return glut.glutGet(glut.GLUT_WINDOW_WIDTH)

        @property
        def height(self):
            return glut.glutGet(glut.GLUT_WINDOW_HEIGHT)

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

        glut.glutReshapeFunc(self._resize_callback)
        glut.glutTimerFunc(int(1000/60), self._timer, fps)
        glut.glutDisplayFunc(self._display)

        glut.glutKeyboardFunc(self._keyboard_callback)
        glut.glutSpecialFunc(self._keyboard_callback)

        glut.glutMotionFunc(self._mouse_callback)
        glut.glutPassiveMotionFunc(self._mouse_callback)

        window.attach_context(self.GlutWindowContext())

        super(GlutApp, self).__init__(**kwargs)

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
        """User defined display handler stub"""

    def _resize_callback(self, width, height):
        gl.glViewport(0, 0, width, height)
        self.on_resize(width, height)

    def on_resize(self, width, height):
        """reshape handler stub"""

    def _timer(self, fps):
        glut.glutTimerFunc(int(1000/fps), self._timer, fps)
        self.timer(fps)
        glut.glutPostRedisplay()

    def timer(self, fps):
        """User-defined timer handler stub"""

    def _keyboard_callback(self, key, *args):
        if self.ENABLE_DEFAULT_KEYBOARD_HOOKS:
            if key == b'\033':
                self.on_exit()

        self.on_key(key, *args)

    def _mouse_callback(self, x, y):
        self.on_mouse_move(x, y)


class GlfwApp(BaseApp):
    class GlfwWindowContext(object):
        def __init__(self, context_window):
            self.context_window = context_window

        @property
        def width(self):
            return glfw.get_window_size(self.context_window)[0]

        @property
        def height(self):
            return glfw.get_window_size(self.context_window)[1]

    def __init__(
        self,
        width=512,
        height=512,
        fps=60,
        window_name='gl2dl rocks!',
        **kwargs
    ):
        compat.enable_glfw_errors_propagation()

        if not glfw.init():
            print("Could not initialize OpenGL context")
            self.on_exit()

        # OS X supports only forward-compatible core profiles from 3.2
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 2)
        glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, 1)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
        # Create a windowed mode window and its OpenGL context

        self.window = glfw.create_window(
            width, height, window_name, None, None
        )
        if not self.window:
            glfw.terminate()
            print("Could not initialize Window")
            self.on_exit()

        # Make the window's context current
        glfw.make_context_current(self.window)
        window.attach_context(self.GlfwWindowContext(self.window))
        glfw.set_key_callback(self.window, self._keyboard_callback)
        glfw.set_cursor_pos_callback(self.window, self._mouse_callback)
        glfw.set_window_size_callback(self.window, self._resize_callback)
        super(GlfwApp, self).__init__(**kwargs)

    def loop(self):
        # Loop until the user closes the window
        while not glfw.window_should_close(self.window):
            # Render here, e.g. using pyOpenGL
            self._display()
            # Poll for and process events
            glfw.poll_events()

        glfw.terminate()
        self.on_exit()

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

    @compat.propagates
    def _keyboard_callback(self, window, key, scancode, action, mods):
        if self.ENABLE_DEFAULT_KEYBOARD_HOOKS:
            if key == 256:
                self.on_exit()

        self.on_key(key, scancode, action, mods)

    @compat.propagates
    def _mouse_callback(self, window, x, y):
        self.on_mouse_move(x, y)

    @compat.propagates
    def _resize_callback(self, window, width, height):
        gl.glViewport(0, 0, width, height)
        self.on_resize(width, height)


