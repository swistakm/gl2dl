# -*- coding: utf-8 -*-
from time import time

from gl2dl.app import App
from gl2dl.sprites import AnimatedSprite


class GLAPP(App):
    def init(self):
        self.sprite = AnimatedSprite((16, 16), 'assets/testtiles.png')

    def display(self):
        try:
            self.clear()
            self.sprite.draw(256, 256, scale=0, frame=time())

        except Exception as err:
            print(err)
            exit(1)


if __name__ == '__main__':
    app = GLAPP()
    app.loop()
