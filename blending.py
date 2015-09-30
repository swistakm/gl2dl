# -*- coding: utf-8 -*-
import contextlib

from functools import partial
import sys
import ctypes
import numpy as np
import OpenGL.GL as gl
import OpenGL.GLUT as glut
import OpenGL.GLU as glu
import OpenGL.arrays.vbo as glvbo


REVERSE_SUBTRACT = gl.GL_FUNC_REVERSE_SUBTRACT
SUBTRACT = gl.GL_FUNC_SUBTRACT
MIN = gl.GL_MIN
MAX = gl.GL_MAX
ADD = gl.GL_FUNC_ADD


@contextlib.contextmanager
def blending_separate(color, alpha):
    gl.glEnable(gl.GL_BLEND)
    gl.glBlendEquationSeparate(color, alpha)

    yield

    gl.glDisable(gl.GL_BLEND)
