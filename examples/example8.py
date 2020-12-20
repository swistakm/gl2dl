# -*- coding: utf-8 -*-
"""
This example shows that there is need to draw rects in batches!
"""
import random
from typing import List

import glfw
from gl2dl.app import GlfwApp
from gl2dl.lights import GLight
from gl2dl.primitives import BaseRect, RectBatch
from gl2dl import blending
from gl2dl.framebuffers import FrameBuffer, FrameBufferTexture
from gl2dl.app import window
from gl2dl.sprites import Sprite


class App(GlfwApp):
    rect_batch: RectBatch
    light: GLight
    static_lights: List[GLight]
    fb: FrameBuffer
    fb_texture: FrameBufferTexture
    lights_sprite: Sprite
    fb_scale: float

    def init(self, size, positions):
        self.rect_batch = RectBatch()

        for pos in positions:
            self.rect_batch.append([pos, BaseRect(*size)])

        occluders = self.rect_batch.get_triangles()

        self.light = GLight((1, 0, 0), (1, 1,), occluders)
        self.static_lights = [
            GLight((0, 1, 0), (100, 100,), occluders),
            GLight((0, 0, 1), (200, 200,), occluders)
        ]

        self.fb = FrameBuffer()
        self.fb_texture = FrameBufferTexture(*glfw.get_framebuffer_size(self.window))
        self.lights_sprite = self.fb_texture.as_sprite()
        self.fb_scale = 1 / (sum(glfw.get_window_content_scale(self.window)) / 2)

    def on_mouse_move(self, x, y):
        y = window.height - y
        self.light.position = x, y

    def display(self):
        self.clear()

        with self.fb.to_texture(self.fb_texture):
            self.clear()

        with self.fb.to_texture(self.fb_texture):
            for light in self.static_lights:
                with blending.blending(mode=blending.Mode.MAX):
                    light.draw()

            with blending.blending(mode=blending.Mode.MAX):
                self.light.draw()
            self.rect_batch.draw()

        self.lights_sprite.draw(0, 0, scale=self.fb_scale)


if __name__ == '__main__':
    size = 10, 10

    positions = [
        (x * random.randint(80, 160), y * random.randint(80, 160))
        for x in range(5)
        for y in range(5)
    ]

    app = App(size=size, positions=positions)
    app.loop()

