# -*- coding: utf-8 -*-
"""
Example of simple animated sprites.

"""
from itertools import cycle
import random
from time import time

from gl2dl.app import App
from gl2dl.blending import alpha_blend
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
            pivot=(32, 0),
            subsheets={
                'walk': [0, 6],
                'balls': [12, 17],
                'jump': [24, 35],
                'smoke': [36, 47],
                'dig': [48, 55],
            }
        )

        self.subsheets = cycle(self.miner.subsheets.keys())
        self.current_subsheet = next(self.subsheets)
        self.flip_x = False
        print(self.current_subsheet)

    def keyboard(self, key, *args):
        self.current_subsheet = next(self.subsheets)
        self.flip_x = random.choice([True, False])

        print("%s: %s" % (
            self.current_subsheet, ['right', 'left'][self.flip_x])
        )

    def display(self):
        try:
            self.clear((.9, .9, .9, 1))
            # for the sake of simplicity we use time
            # as a source of frames
            self.numbers.draw(256, 256, scale=4, frame=time())
            with alpha_blend():
                self.miner.draw(
                    256, 256 + 8 * 4,
                    frame=time()*10,
                    subsheet=self.current_subsheet,
                    flip_x=self.flip_x
                )

        except Exception as err:
            print(err)
            exit(1)


if __name__ == '__main__':
    GLAPP().loop()
