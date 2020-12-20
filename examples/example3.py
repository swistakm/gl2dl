from gl2dl.app import GlfwApp
from gl2dl.sprites import Sprite


class GLAPP(GlfwApp):
    sprite: Sprite

    def init(self):
        self.sprite = Sprite('assets/marble.png', pivot=(128, 128))

    def display(self):
        self.clear()
        self.sprite.draw(x=256, y=256, scale=1)


if __name__ == '__main__':
    GLAPP().loop()
