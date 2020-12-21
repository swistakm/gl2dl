# -*- coding: utf-8 -*-
"""
This example shows that there is need to draw rects in batches!
"""

import numpy as np

from gl2dl.app import GlfwApp
from gl2dl.lights import GLight
from gl2dl.primitives import Rect, Triangles


class App(GlfwApp):
    rect: Rect
    light: GLight
    triangles: Triangles

    def init(self):
        data = np.array(
            [
                ([100, 0],   [1, 0, 0, 1]),
                ([0,   100], [0, 1, 0, 1]),
                ([100, 100], [0, 0, 1, 1]),

                ([20, 40],   [.7, 0,   .1, .5]),
                ([40, 40],   [.1, 0.5, .1, .5]),
                ([40, 20],   [.1, 0,    1, .5]),
            ],
            dtype=[("position", np.float32, 2), ("color", np.float32, 4)]
        )
        self.triangles = Triangles(data)

    def display(self):
        self.clear()
        self.triangles.draw()


if __name__ == '__main__':
    App().loop()
