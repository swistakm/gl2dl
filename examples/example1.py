# -*- coding: utf-8 -*-
import random

import OpenGL.GL as gl
import OpenGL.GLUT as glut

import numpy as np

from gl2dl.app import App
from gl2dl.shaders import ShaderProgram
from gl2dl.lights import GLight
from gl2dl.primitives import rect_triangles, ortho

# Vertex shader
VS = """
#version 330 core
layout(location = 0) in vec2 position;

uniform vec3 wall_color;
uniform mat4 model_view_projection;

out vec4 vertex_color;
out vec2 vertex_position;

void main()
{
    gl_Position = model_view_projection * vec4(position.xy, 0, 1);

    vertex_position = position;
    vertex_color = vec4(wall_color, 1);
}
"""

# Fragment shader
FS = """
#version 330 core
uniform vec2 light_position;

out lowp vec4 out_color;

in vec2 vertex_position;
in vec4 vertex_color;

void main()
{
    float distance = length(light_position - gl_FragCoord.xy);
    float attenuation = 300 / pow(distance, 1);

    out_color = vec4(
        attenuation,
        attenuation,
        attenuation,
        1
    ) * vertex_color;
}
"""


class GLAPP(App):
    def init(self, data=None):
        self.shader = ShaderProgram(VS, FS)
        self.data = data

        self.VAO = gl.glGenVertexArrays(1)
        gl.glBindVertexArray(self.VAO)

        self.VBO = gl.glGenBuffers(1)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.VBO)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, data.nbytes, data, gl.GL_STATIC_DRAW)
        gl.glEnableVertexAttribArray(0)

        self.light = GLight((1, .5, .5), (0, 0,), data)

    def on_mouse_move(self, x, y):
        self.light.color = 1, 0, 1
        self.light.position = x, glut.glutGet(glut.GLUT_WINDOW_HEIGHT) - y
        self.light.radius = 200

        with self.shader as active:
            active['light_position'] = self.light.position

    def timer(self, fps):
        randsign = lambda: [1, -1][random.randint(0, 1)]
        self.light.radius += random.random() * 2 * randsign()

    def loop(self):
        with self.shader as active:
            active['wall_color'] = .8, .8, .8

        super(GLAPP, self).loop()

    def display(self):
        try:
            # TODO: implement rendering merged lights to framebuffer and
            #       blending them as texture (maybe LightingScene?)
            # gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, self.FBO)
            self.clear()
            self.light.draw()

            # draw occluders polygons
            gl.glBindVertexArray(self.VAO)
            gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.VBO)
            gl.glVertexAttribPointer(0, 2, gl.GL_FLOAT, gl.GL_FALSE, 0, None)

            with self.shader as active:
                active['model_view_projection'] = ortho(
                    glut.glutGet(glut.GLUT_WINDOW_WIDTH),
                    glut.glutGet(glut.GLUT_WINDOW_HEIGHT),
                )
                gl.glDrawArrays(gl.GL_TRIANGLES, 0, len(self.data))

        except Exception as err:
            print err
            exit(1)


if __name__ == '__main__':
    data = np.array([], dtype=np.float32)

    data = np.append(data, rect_triangles(50, 50, 100, 100))
    data = np.append(data, rect_triangles(150, 50, 220, 200))
    data = np.append(data, rect_triangles(20, 300, 100, 350))

    GLAPP(data=data).loop()
