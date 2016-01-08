# -*- coding: utf-8 -*-
import sys
import OpenGL.GL as gl
import OpenGL.GLUT as glut

import numpy as np
from app import App

from shaders import ShaderProgram
from lights import GLight

# Vertex shader
VS = """
#version 330 core
layout(location = 0) in vec2 position;

uniform vec3 wall_color;

out vec4 vertex_color;
out vec2 vertex_position;

void main()
{
    gl_Position = vec4(position.xy, 0, 1);

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
    float distance = distance(light_position, vertex_position);
    float attenuation = 0.2 / pow(distance, 5);

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

        # -- start fbo and texture target --
        self.FBO_TARGET = gl.glGenTextures(1)
        # "Bind" the newly created texture : all future texture functions
        # will modify this texture
        gl.glBindTexture(gl.GL_TEXTURE_2D, self.FBO_TARGET)
        # Give an empty image to OpenGL ( the last "0" )
        gl.glTexImage2D(
            gl.GL_TEXTURE_2D, 0, gl.GL_RGBA,
            1024, 768, 0, gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, None
        )
        # Poor filtering. Needed !
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_NEAREST)
        gl.glBindTexture(gl.GL_TEXTURE_2D, 0)

        # TODO: implement some kind of FBO object to simplify this
        # Set "renderedTexture" as our colour attachement #0
        self.FBO = gl.glGenFramebuffers(1)
        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, self.FBO)
        gl.glFramebufferTexture(
            gl.GL_FRAMEBUFFER, gl.GL_COLOR_ATTACHMENT0, self.FBO_TARGET, 0
        )

        status = gl.glCheckFramebufferStatus(gl.GL_FRAMEBUFFER)

        if status != gl.GL_FRAMEBUFFER_COMPLETE:
            print "framebuffer status failed"
            exit()
        else:
            print "framebuffer status", status
        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, 0)
        # -- end fbo --

        self.light = GLight((1, .5, .5), (0, 0, 0), data)

    def on_mouse_move(self, x, y):
        self.light.color = 1, 0, 1
        self.light.position = (
            float(x - self.width/2) / self.width,
            float(self.height/2 - y) / self.height,
        )
        self.light.radius = 0.1

        self.shader.bind()
        self.shader['light_position'] = self.light.position

    def timer(self, fps):
        glut.glutTimerFunc(1000/fps, self.timer, fps)
        glut.glutPostRedisplay()

    def loop(self):
        with self.shader as uniforms:
            uniforms['wall_color'] = .8, .8, .8

        super(GLAPP, self).loop()

    def display(self):
        # clear the buffer
        gl.glClearColor(0, 0, 0, 0)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)

        try:
            # TODO: implement rendering merged lights to framebuffer and
            #       blending them as texture (maybe LightingScene?)
            # gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, self.FBO)
            gl.glClearColor(0, 0, 0, 0)
            gl.glClear(gl.GL_COLOR_BUFFER_BIT)

            # draw lights
            self.light.draw()

            # draw occluders polygons
            gl.glBindVertexArray(self.VAO)
            gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.VBO)
            gl.glVertexAttribPointer(0, 2, gl.GL_FLOAT, gl.GL_FALSE, 0, None)

            self.shader.bind()
            gl.glDrawArrays(gl.GL_TRIANGLES, 0, len(self.data))

        except Exception as err:
            print err
            exit(1)

        finally:
            gl.glBindVertexArray(0)
            gl.glUseProgram(0)

            gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)
            gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, 0)

            glut.glutSwapBuffers()

    @staticmethod
    def keyboard(key, *args):
        if key == '\033':
            sys.exit()


if __name__ == '__main__':
    data = np.array([], dtype=np.float32)

    magic_number = 4

    for w in xrange(-magic_number, magic_number):
        for i in xrange(-magic_number, magic_number):
            hole = np.array([
                [-1, -1],
                [-1, 1],
                [1, 1],

                [1, -1],
                [1, 1],
                [-1, -1],
            ], dtype=np.float32) / (magic_number * 10)

            hole += i/(magic_number * 1.2), w/(magic_number * 1.2)
            data = np.append(data, hole)

    GLAPP(data=data).loop()
