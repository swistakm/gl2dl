from time import time
from math import sin, cos

from gl2dl.app import GlfwApp
from gl2dl.sprites import Sprite


class App(GlfwApp):
    sprite: Sprite

    def init(self):
        self.sprite = Sprite('assets/heart.png', pivot=(270, 160))

    def display(self):
        self.clear()

        self.sprite.draw(
            x=sin(time()) * 128 + 256,
            y=cos(time()) * 128 + 256,
            scale=sin(time() * 50) / 50 + .5
        )


if __name__ == '__main__':
    App().loop()
