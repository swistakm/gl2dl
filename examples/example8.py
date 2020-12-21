"""
This example shows that there is need to draw rects in batches!
"""
import math
import random
import time
from typing import List

import glfw
from gl2dl.app import GlfwApp
from gl2dl.lights import GLight
from gl2dl.primitives import BaseRect, RectBatch
from gl2dl import blending
from gl2dl.framebuffers import FrameBuffer, FrameBufferTexture
from gl2dl.app import window


class App(GlfwApp):
    rect_batch: RectBatch
    light: GLight
    static_lights: List[GLight]

    fb: FrameBuffer
    final_fb_texture: FrameBufferTexture
    temp_fb_texture: FrameBufferTexture

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
        self.final_fb_texture = FrameBufferTexture(*glfw.get_framebuffer_size(self.window))
        self.temp_fb_texture = FrameBufferTexture(*glfw.get_framebuffer_size(self.window))

        self.fb_scale = 1 / (sum(glfw.get_window_content_scale(self.window)) / 2)

    def on_mouse_move(self, x, y):
        y = window.height - y
        self.light.position = x, y

    def display(self):
        self.clear()

        with self.fb.to_texture(self.final_fb_texture):
            self.clear()

        for i, light in enumerate(self.static_lights + [self.light]):
            light.intensity = 1 + math.sin(time.time()*10+i*10) / 4 - 0.25
            with self.fb.to_texture(self.temp_fb_texture):
                light.draw()

            with self.fb.to_texture(self.final_fb_texture):
                with blending.blending(mode=blending.Mode.MAX):
                    self.temp_fb_texture.as_sprite().draw(scale=self.fb_scale)

        self.final_fb_texture.as_sprite().draw(scale=self.fb_scale)
        self.rect_batch.draw()


if __name__ == '__main__':
    size = 3, 3

    positions = [
        (x * random.randint(0, 160), y * random.randint(0, 160))
        for x in range(50)
        for y in range(50)
    ]

    app = App(size=size, positions=positions)
    app.loop()

