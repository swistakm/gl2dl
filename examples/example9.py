# -*- coding: utf-8 -*-
"""
Example of simple animated sprites.

"""
from time import time

from gl2dl.app import App
from gl2dl.sprites import AnimatedSprite


class GLAPP(App):
    def init(self):
        self.numbers = AnimatedSprite(
            # our spritesheet consists of 16x16 squares
            (16, 16),
            # and is implicely loaded from file
            'assets/numbers.png',
            # we set pivot in the centre of its dimensions
            pivot=(8, 8),
        )
        self.miner = AnimatedSprite(
            (64, 64),
            'assets/miner_animation.png',
            pivot=(32, 0)
        )

    def display(self):
        try:
            self.clear()
            # for the sake of simplicity we use time
            # as a source of frames
            self.numbers.draw(256, 256, scale=1, frame=time() * 3)
            self.miner.draw(256, 256 + 8, frame=time() * 10)

        except Exception as err:
            print(err)
            exit(1)


if __name__ == '__main__':
    GLAPP().loop()
