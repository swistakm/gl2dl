# -*- coding: utf-8 -*-
import traceback
import sys

from gl2dl.app import GlutApp
from gl2dl.sprites import Sprite


class GLAPP(GlutApp):
    def init(self):
        self.sprite = Sprite('assets/marble.png', pivot=(128, 128))

    def display(self):
        try:
            self.clear()
            self.sprite.draw(x=256, y=256, scale=1)

        except Exception as err:
            traceback.print_exc(file=sys.stdout)
            exit(1)


if __name__ == '__main__':
    GLAPP().loop()
