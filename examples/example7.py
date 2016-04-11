# -*- coding: utf-8 -*-
"""
This example shows that there is need to draw rects in batches!
"""
import random

import OpenGL.GLUT as glut

from gl2dl.app import App
from gl2dl.lights import GLight, ShadowMap
from gl2dl.primitives import BaseRect, RectBatch


class GLAPP(App):
    def init(self, size, positions):
        self.rect_batch = RectBatch()

        for pos in positions:
            self.rect_batch.append([pos, BaseRect(*size)])

        occluders = self.rect_batch.get_triangles()
        self.light = GLight((1, .5, .5), (0, 0,), occluders)

    def on_mouse_move(self, x, y):
        self.light.color = 1, 0, 1
        self.light.position = x, glut.glutGet(glut.GLUT_WINDOW_HEIGHT) - y
        self.light.radius = 200

    def loop(self):
        super(GLAPP, self).loop()

    def display(self):

        # # experimental
        # for row in self.rect_batch:
        #     pos = row[0]
        #     row[0] = (
        #         pos[0] + random.randint(-1, 1),
        #         pos[1] + random.randint(-1, 1),
        #     )
        #
        # self.light._shadows = ShadowMap(self.rect_batch.get_triangles())
        # self.light._shadows.position = self.light.position

        try:
            self.clear()
            self.light.draw()
            self.rect_batch.draw()

        except Exception as err:
            print(err)
            exit(1)

if __name__ == '__main__':
    size = 5, 5

    positions = [
        (x * 10, y * 10) for x in range(50) for y in range(50)
    ]

    GLAPP(size=size, positions=positions).loop()
