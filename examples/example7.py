import random
from time import time
from math import cos, sin, sqrt

from gl2dl.app import GlfwApp
from gl2dl.lights import GLight, ShadowMap
from gl2dl.primitives import BaseRect, RectBatch
from gl2dl.app import window


class App(GlfwApp):
    rect_batch: RectBatch
    light: GLight

    def init(self, size, positions):
        self.rect_batch = RectBatch()

        for pos in positions:
            self.rect_batch.append([pos, BaseRect(*size)])
        occluders = self.rect_batch.get_triangles()

        self.light = GLight((1, 0, 0), (1, 1,), occluders, radius=200)

    def on_mouse_move(self, x, y):
        y = window.height - y
        delta = sqrt(x ** 2 + y ** 2) / 100

        self.light.color = abs(sin(delta)), abs(cos(delta)), abs(sin(delta))
        self.light.position = x, y

    def display(self):
        for seed, row in enumerate(self.rect_batch):
            r = random.Random(seed)

            pos = row[0]
            row[0] = (
                pos[0] + sin(time() * 10 * r.random()),
                pos[1] + cos(time() * 10 * r.random()),
            )

        self.light._shadows = ShadowMap(self.rect_batch.get_triangles())
        self.light._shadows.position = self.light.position

        self.clear()
        self.light.draw()
        self.rect_batch.draw()


if __name__ == '__main__':
    size = 1, 1

    positions = [
        (x * random.randint(20, 40), y * random.randint(20, 40))
        for x in range(20)
        for y in range(20)
    ]

    app = App(size=size, positions=positions)
    app.loop()

