# -*- coding: utf-8 -*-
from contextlib import contextmanager

import OpenGL.GL as gl


class Mode(object):
    REVERSE_SUBTRACT = gl.GL_FUNC_REVERSE_SUBTRACT
    SUBTRACT = gl.GL_FUNC_SUBTRACT
    MIN = gl.GL_MIN
    MAX = gl.GL_MAX
    ADD = gl.GL_FUNC_ADD


class Factor(object):
    ZERO = gl.GL_ZERO
    ONE = gl.GL_ONE
    SRC_COLOR = gl.GL_SRC_COLOR
    ONE_MINUS_SRC_COLOR = gl.GL_ONE_MINUS_SRC_COLOR
    DST_COLOR = gl.GL_DST_COLOR
    ONE_MINUS_DST_COLOR = gl.GL_ONE_MINUS_DST_COLOR
    SRC_ALPHA = gl.GL_SRC_ALPHA
    ONE_MINUS_SRC_ALPHA = gl.GL_ONE_MINUS_SRC_ALPHA
    DST_ALPHA = gl.GL_DST_ALPHA
    ONE_MINUS_DST_ALPHA = gl.GL_ONE_MINUS_DST_ALPHA
    CONSTANT_COLOR = gl.GL_CONSTANT_COLOR

    ONE_MINUS_CONSTANT_COLOR = gl.GL_ONE_MINUS_CONSTANT_COLOR
    CONSTANT_ALPHA = gl.GL_CONSTANT_ALPHA
    ONE_MINUS_CONSTANT_ALPHA = gl.GL_ONE_MINUS_CONSTANT_ALPHA


@contextmanager
def blending_rgba(
        rgb_source=Factor.ONE,
        rgb_destination=Factor.ZERO,

        alpha_source=Factor.ONE,
        alpha_destination=Factor.ZERO,

        rgb_mode=Mode.ADD,
        alpha_mode=Mode.ADD,
):
    """ **Important:** does not support nesting yet

    TODO: support nesting by remembering the state of GL_BLEND (see blending)
    :param rgb_source:
    :param rgb_destination:
    :param alpha_source:
    :param alpha_destination:
    :param rgb_mode:
    :param alpha_mode:

    """
    gl.glEnable(gl.GL_BLEND)
    gl.glBlendEquationSeparate(rgb_mode, alpha_mode)
    gl.glBlendFuncSeparate(
        rgb_source, rgb_destination,
        alpha_source, alpha_destination
    )

    yield

    gl.glDisable(gl.GL_BLEND)


@contextmanager
def blending(
        source=Factor.ONE,
        destination=Factor.ZERO,
        mode=Mode.ADD,
):
    """
    :param source:
    :param destination:
    :param mode:

    """
    enabled = gl.glGetBoolean(gl.GL_BLEND)
    old_mode = gl.glGetInteger(gl.GL_BLEND_EQUATION)
    old_source = gl.glGetInteger(gl.GL_BLEND_SRC)
    old_destination = gl.glGetInteger(gl.GL_BLEND_DST)

    if not enabled:
        gl.glEnable(gl.GL_BLEND)

    gl.glBlendEquation(mode)
    gl.glBlendFunc(source, destination)

    try:
        yield

    finally:
        if enabled:
            gl.glBlendEquation(old_mode)
            gl.glBlendFunc(old_source, old_destination)
        else:
            gl.glDisable(gl.GL_BLEND)

