from time import time
from math import sin, cos

import imgui

import glfw
from gl2dl.app import ImguiApp
from gl2dl.framebuffers import FrameBuffer, FrameBufferTexture
from gl2dl.sprites import Sprite, AnimatedSprite


class App(ImguiApp):
    heart: Sprite
    miner: AnimatedSprite

    fb: FrameBuffer
    fb_texture: FrameBufferTexture
    fb_scale: float

    def init(self):
        self.heart = Sprite('assets/heart.png', pivot=(270, 160))
        self.miner = AnimatedSprite(
            (64, 64), 'assets/miner_animation.png',
            pivot=(32, 0),
            subsheets={
                'walk': [0, 6],
                'balls': [12, 17],
                'jump': [24, 35],
                'smoke': [36, 47],
                'dig': [48, 55],
            }
        )
        self.fb = FrameBuffer()
        self.fb_texture = FrameBufferTexture(*glfw.get_framebuffer_size(self.window))
        self.fb_scale = 1 / (sum(glfw.get_window_content_scale(self.window)) / 2)

    def display(self):
        self.clear()

        self.heart.draw(
            x=sin(time()) * 128 + 256,
            y=cos(time()) * 128 + 256,
            scale=sin(time() * 50) / 50 + .5
        )

        imgui.begin("Sprites")
        imgui.text("assets/heart.png")
        imgui.image(self.heart.texture_id, self.heart.width / 2, self.heart.height / 2, (0, 1), (1, 0))
        imgui.text("assets/miner_animation.png")
        imgui.image(self.miner.texture_id, self.heart.width / 2, self.heart.height / 2, (0, 1), (1, 0))

        with self.fb.to_texture(self.fb_texture):
            self.clear()
            self.heart.draw(
                x=sin(time()) * 128 + 256,
                y=cos(time()) * 128 + 256,
                scale=sin(time() * 50) / 50 + .5
            )

        self.fb_texture.as_sprite().draw(scale=self.fb_scale)

        imgui.text("viewport")
        imgui.image(self.fb_texture.texture, self.fb_texture.width / 4, self.fb_texture.height / 4, (0, 1), (1, 0))

        imgui.end()


if __name__ == '__main__':
    App(width=800, height=800).loop()
