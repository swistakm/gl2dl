# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
from time import time
from math import sin, cos

from gl2dl.app import App
from gl2dl.primitives import Rect


class GLAPP(App):
    def init(self, data=None):
        self.data = data
        self.rect = Rect(100, 50, pivot=(50, 25))

    def display(self):
        try:
            self.clear()

            self.rect.draw(
                x=sin(time()) * 128 + 256,
                y=cos(time()) * 128 + 256,
                scale=sin(time() * 5) / 2. + 1,
                color=(
                    (sin(time() * 10) + 1) / 2.,
                    (cos(time() * 5.) + 1) / 2.,
                    (sin(time() * 3.) + 1) / 2.,
                )
            )

        except Exception as err:
            print(err)
            exit(1)

if __name__ == '__main__':
    GLAPP().loop()
