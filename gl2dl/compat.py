# -*- coding: utf-8 -*-
from functools import wraps
import sys

import glfw

# fixme: it is not thread safe, try to use Lock, dict, and thread.get_indent()
# note: wont be needed when https://github.com/FlorianRhiem/pyGLFW/issues/12
#       gets fixed/accepted
_glfw_errors = [None]


def _errcheck(result, func, args):
    if _glfw_errors[0] is not None:
        _glfw_errors[0], error = None, _glfw_errors[0]
        if isinstance(error, tuple):
            raise error[0], error[1], error[2]
        else:
            raise error

    return result


def _glfw_error_callback(err, description):
    _glfw_errors[0] = RuntimeError("GLFW error (%s): %s" % (err, description))


def enable_glfw_errors_propagation():
    for function in glfw._glfw.__dict__.values():
        if hasattr(function, 'errcheck'):
            function.errcheck = _errcheck

    glfw.set_error_callback(_glfw_error_callback)


def propagates(event_handler):
    @wraps(event_handler)
    def propagator(*args, **kwargs):
        try:
            event_handler(*args, **kwargs)
        except Exception as err:
            _glfw_errors[0] = sys.exc_info()

    return propagator
