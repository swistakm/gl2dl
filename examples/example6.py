# -*- coding: utf-8 -*-
"""
This example shows that there is need to draw rects in batches!
"""

import OpenGL.GLUT as glut

import numpy as np

from gl2dl.app import App
from gl2dl.lights import GLight
from gl2dl.primitives import rect_triangles, Rect


class GLAPP(App):
    def init(self, size, positions):
        self.rect = Rect(*size)

        occluders = np.array([], dtype=np.float32)

        for pos in positions:
            occluders = np.append(occluders, rect_triangles(
                pos[0], pos[1],
                pos[0] + self.rect.width, pos[1] + self.rect.height
                )
            )

        self.light = GLight((1, .5, .5), (0, 0,), occluders)

    def on_mouse_move(self, x, y):
        self.light.color = 1, 0, 1
        self.light.position = x, glut.glutGet(glut.GLUT_WINDOW_HEIGHT) - y
        self.light.radius = 200

    def loop(self):
        super(GLAPP, self).loop()

    def display(self):
        try:
            self.clear()
            self.light.draw()
            for position in positions:
                self.rect.draw(*position, color=(1, 1, 1))

        except Exception as err:
            print(err)
            exit(1)

if __name__ == '__main__':
    size = 20, 20

    positions = [
        (x * 50, y * 50) for x in range(10) for y in range(10)
    ]

    GLAPP(size=size, positions=positions).loop()
