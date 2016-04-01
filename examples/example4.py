# -*- coding: utf-8 -*-
from time import time
from math import sin, cos

from gl2dl.app import App
from gl2dl.sprites import Sprite


class GLAPP(App):
    def init(self):
        self.sprite = Sprite('assets/heart.jpg', pivot=(270, 160))

    def display(self):
        try:
            self.clear()

            self.sprite.draw(
                x=sin(time()) * 128 + 256,
                y=cos(time()) * 128 + 256,
                scale=sin(time() * 50) / 50 + .5
            )

        except Exception as err:
            print err
            exit(1)


if __name__ == '__main__':
    GLAPP().loop()
