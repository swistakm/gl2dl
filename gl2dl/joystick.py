# -*- coding: utf-8 -*-
from collections import namedtuple

import glfw

from .compat import propagates

JOYSTICK_0 = 0
JOYSTICK_1 = 1
JOYSTICK_2 = 2
JOYSTICK_3 = 3
JOYSTICK_4 = 4
JOYSTICK_5 = 5
JOYSTICK_6 = 6
JOYSTICK_7 = 7
JOYSTICK_8 = 8
JOYSTICK_9 = 9
JOYSTICK_10 = 10
JOYSTICK_11 = 11
JOYSTICK_12 = 12
JOYSTICK_13 = 13
JOYSTICK_14 = 14
JOYSTICK_15 = 15
JOYSTICK_LAST = JOYSTICK_15

DISCONNECTED = False
CONNECTED = True


# note: only xbox pad layout right now
ButtonsTuple = namedtuple("ButtonsTuple", [
    "a_button",
    "b_button",
    "x_button",
    "y_button",
    "left_bumper",
    "right_bumper",
    "back_button",
    "start_button",
    "left_stick",
    "right_stick",
    "dpad_up",
    "dpad_right",
    "dpad_down",
    "dpad_left",
])
# note: make ButtonsTuple initializable with 0 arguments so it
#       can be easily used for dispatching specific button events
ButtonsTuple.__new__.__defaults__ = tuple(0 for field in ButtonsTuple._fields)

AxesTuple = namedtuple("AxesTuple", [
    "left_stick_x",
    "left_stick_y",
    "right_stick_x",
    "right_stick_y",
    "left_trigger",
    "right_trigger",
])


class JoystickNotPresent(RuntimeError):
    """ Raised when joystick is not present but queried for state
    """


class JoystickCapture(object):
    def __init__(self, state_callback=None, button_callback=None):
        self._state_callback = state_callback
        self._button_callback = button_callback

    def set_state_callback(self, callback):
        self._state_callback = callback

    def poll_events(self):
        raise NotImplementedError

    def get_connected_joysticks(self):
        raise NotImplementedError

    def get_axes(self, joystick):
        raise NotImplementedError

    def get_buttons(self, joystick):
        raise NotImplementedError


class GlfwJoystickCapture(JoystickCapture):
    GLFW_TO_JOYSTICK = {
        glfw.JOYSTICK_1: 0,
        glfw.JOYSTICK_2: 1,
        glfw.JOYSTICK_3: 2,
        glfw.JOYSTICK_4: 3,
        glfw.JOYSTICK_5: 4,
        glfw.JOYSTICK_6: 5,
        glfw.JOYSTICK_7: 6,
        glfw.JOYSTICK_8: 7,
        glfw.JOYSTICK_9: 8,
        glfw.JOYSTICK_10: 9,
        glfw.JOYSTICK_11: 10,
        glfw.JOYSTICK_12: 11,
        glfw.JOYSTICK_13: 12,
        glfw.JOYSTICK_14: 13,
        glfw.JOYSTICK_15: 14,
        glfw.JOYSTICK_16: 15,
    }

    JOYSTICK_TO_GLFW = {
        value: key for key, value in GLFW_TO_JOYSTICK.items()
    }

    GLFW_TO_EVENT = {
        glfw.DISCONNECTED: DISCONNECTED,
        glfw.CONNECTED: CONNECTED,
    }

    def __init__(self, state_callback=None, button_callback=None):
        super(GlfwJoystickCapture, self).__init__(
            state_callback, button_callback
        )
        # note: this is only internal callback, user callback was already
        #       set by super().__init__
        glfw.set_joystick_callback(self._joystick_callback)

        self._connected_joysticks = {
            joystick: ButtonsTuple()
            for joystick in self.get_connected_joysticks()
        }

    @propagates
    def _joystick_callback(self, glfw_joystick, glfw_state):
        """ Interanal GLFW joystick state change handler

        :param glfw_joystick: glfw's joystick index (from glfw constant)
        :param glfw_state: glfw's joystick state (from glfw constant)

        :return: DISCONNECTED (False) or CONNECTED (True) value
        """
        joystick = self.GLFW_TO_JOYSTICK[glfw_joystick]
        state = self.GLFW_TO_EVENT[glfw_state]

        if state and joystick not in self._connected_joysticks:
            self._connected_joysticks[joystick] = ButtonsTuple()
        elif not state and joystick in self._connected_joysticks:
            del self._connected_joysticks[joystick]

        if self._state_callback is not None:
            self._state_callback(joystick, state)

    def get_connected_joysticks(self):
        return [
            joystick for joystick, glfw_joystick
            in self.JOYSTICK_TO_GLFW.items()
            if glfw.joystick_present(glfw_joystick)
        ]

    def get_state(self, joystick):
        glfw_joystick = self.JOYSTICK_TO_GLFW[joystick]

        return bool(glfw.joystick_present(glfw_joystick))

    def get_axes(self, joystick):
        glfw_joystick = self.JOYSTICK_TO_GLFW[joystick]

        if not glfw.joystick_present(glfw_joystick):
            raise JoystickNotPresent

        ctypes_axes, count = glfw.get_joystick_axes(glfw_joystick)
        return AxesTuple(*ctypes_axes[0:count])

    def get_buttons(self, joystick):
        glfw_joystick = self.JOYSTICK_TO_GLFW[joystick]

        if not glfw.joystick_present(glfw_joystick):
            raise JoystickNotPresent

        ctypes_buttons, count = glfw.get_joystick_buttons(glfw_joystick)
        return ButtonsTuple(*ctypes_buttons[0:count])

    def poll_events(self):
        if self._button_callback is None:
            # if there is no button callback then there is no need
            # to poll events - quit early to save time
            return

        # fixme: this will inevitably fail on python3 because dictionary
        # fixme: self._connected_joysticks may indirectly change size
        # fixme: if glfw somhwhere in the middle will try to poll
        # fixme: and will trigger joystick state change callback
        # note: possible solution -> create separate dict for all new states
        #       and compare values afterwards
        for joystick, old_state in self._connected_joysticks.items():
            try:
                new_state = self.get_buttons(joystick)
            except JoystickNotPresent:
                continue

            for (new, old, button) in zip(
                new_state, old_state, ButtonsTuple._fields
            ):
                if new != old:
                    try:
                        self._button_callback(joystick, button, new)
                    finally:
                        self._connected_joysticks[joystick] = new_state
