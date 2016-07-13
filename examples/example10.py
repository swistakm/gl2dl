# -*- coding: utf-8 -*-
"""
Example of simple animated sprites.

"""
import traceback
import sys


from gl2dl.app import GlutApp, GlfwApp
from gl2dl.joystick import GlfwJoystickCapture


class GLAPP(GlfwApp):
    def init(self):
        self.joys = GlfwJoystickCapture(
            state_callback=self.on_joystick_state_change,
            button_callback=self.on_joystick_button
        )

    def on_joystick_button(self, joystick, button, value):
        print(joystick, button, value)

    def on_joystick_state_change(self, joystick, state):
        print(joystick, state)

    def display(self):
        # josticks = self.joys.get_connected_joysticks()
        # if josticks:
        #     print(self.joys.get_buttons(josticks[0]))

        self.joys.poll_events()

        try:
            self.clear((.9, .9, .9, 1))

        except Exception as err:
            traceback.print_exc(file=sys.stdout)
            exit(1)

if __name__ == '__main__':
    GLAPP().loop()
