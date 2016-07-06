# -*- coding: utf-8 -*-
"""
This example shows that there is need to draw rects in batches!
"""
import random

import OpenGL.GLUT as glut

from gl2dl.app import App
from gl2dl.lights import GLight
from gl2dl.primitives import BaseRect, RectBatch
from gl2dl import blending
from gl2dl.framebuffers import FrameBuffer, FrameBufferTexture


class GLAPP(App):
    def init(self, size, positions):
        self.rect_batch = RectBatch()

        for pos in positions:
            self.rect_batch.append([pos, BaseRect(*size)])

        occluders = self.rect_batch.get_triangles()

        self.mouse_light = GLight((1, 0, 0), (1, 1,), occluders)
        self.static_lights = [
            GLight((0, 1, 0), (100, 100,), occluders),
            GLight((0, 0, 1), (400, 100,), occluders)
        ]

        self.framebuffer = FrameBuffer()
        self.fb_texture = FrameBufferTexture(512, 512)
        self.lights_sprite = self.fb_texture.drawable()

    def on_mouse_move(self, x, y):
        self.mouse_light.position = x, glut.glutGet(glut.GLUT_WINDOW_HEIGHT) - y

    def loop(self):
        super(GLAPP, self).loop()

    def display(self):
        try:
            self.clear()

            with self.framebuffer.to_texture(self.fb_texture):
                self.mouse_light.draw()

            self.lights_sprite.draw(0, 0, scale=1)

            for light in self.static_lights:
                with self.framebuffer.to_texture(self.fb_texture):
                    light.draw()

                with blending.blending(mode=blending.Mode.MAX):
                    self.lights_sprite.draw(0, 0, scale=1)

            # note: we are drawing only boxes so no blending required
            self.rect_batch.draw()

        except Exception as err:
            print(err)
            exit(1)


if __name__ == '__main__':
    size = 10, 10

    positions = [
        (x * random.randint(80, 160), y * random.randint(80, 160))
        for x in range(5)
        for y in range(5)
    ]

    app = GLAPP(size=size, positions=positions)

    app.loop()

