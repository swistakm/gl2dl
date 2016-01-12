# -*- coding: utf-8 -*-
from app import App
from sprites import Sprite


class GLAPP(App):
    def init(self):
        self.sprite = Sprite('marble.bmp', pivot=(128, 128))

    def display(self):
        try:
            self.clear()
            self.sprite.draw(x=256, y=256, scale=1)

        except Exception as err:
            print err
            exit(1)


if __name__ == '__main__':
    GLAPP().loop()
