# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
import sys

import OpenGL.GL as gl
import OpenGL.GLUT as glut

from PIL import Image
import numpy as np
from shaders import ShaderProgram


VS = """
#version 330 core

// Input vertex data, different for all executions of this shader.
layout(location = 0) in vec2 vertexPosition;
layout(location = 1) in vec2 vertexUV;

// Output data ; will be interpolated for each fragment.
out vec2 UV;

void main(){
    gl_Position =  vec4(vertexPosition, 0, 1);
    // UV of the vertex. No special space for this one.
    UV = vertexUV;
}
"""


FS = """
#version 330 core

// Interpolated values from the vertex shaders
in vec2 UV;

// Ouput data
out vec3 color;

// Values that stay constant for the whole mesh.
uniform sampler2D texture_sampler;

void main(){

    // Output color = color of the texture at the specified UV
    color = texture(texture_sampler, UV ).rgb;
 //   color = vec3(UV, 0);
}
"""


class GLAPP(object):
    def __init__(self, data):
        self.width = 512
        self.height = 512
        glut.glutInit()
        glut.glutInitDisplayMode(
            # note: glut.GLUT_3_2_CORE_PROFILE is for Mac OS X
            glut.GLUT_DOUBLE | glut.GLUT_RGBA | glut.GLUT_3_2_CORE_PROFILE
        )
        glut.glutCreateWindow('Hello world!')
        glut.glutReshapeWindow(self.width, self.height)

        self.data = data

        glut.glutReshapeFunc(self.reshape)
        glut.glutKeyboardFunc(self.keyboard)
        glut.glutDisplayFunc(self.display)

        glut.glutTimerFunc(1000/60, self.timer, 60)
        glut.glutMotionFunc(self.on_mouse_move)
        glut.glutPassiveMotionFunc(self.on_mouse_move)

        self.VAO = gl.glGenVertexArrays(1)
        gl.glBindVertexArray(self.VAO)

        self.VBO = gl.glGenBuffers(1)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.VBO)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, data.nbytes, data, gl.GL_STATIC_DRAW)
        gl.glEnableVertexAttribArray(0)

        self.image = Image.open('marble.bmp')
        self.texture = gl.glGenTextures(1)

        gl.glBindTexture(gl.GL_TEXTURE_2D, self.texture)
        # note: check what it does!
        gl.glPixelStorei(gl.GL_UNPACK_ALIGNMENT, 1)

        ix = self.image.size[0]
        iy = self.image.size[1]
        image_bytes = self.image.tobytes("raw", "RGBX", 0, -1)

        gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGB, ix, iy, 0, gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, image_bytes)

        gl.glTexParameter(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)
        gl.glTexParameter(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_NEAREST)

        self.uv_data = np.array([
            [0, 0],
            [0, 1],
            [1, 1],

            [1, 0],
            [1, 1],
            [0, 0],

        ], dtype=np.float32)

        self.UVB = gl.glGenBuffers(1)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.UVB)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, self.uv_data.nbytes, self.uv_data, gl.GL_STATIC_READ)
        # note: location of buffer?
        gl.glEnableVertexAttribArray(1)

        self.shader = ShaderProgram(VS, FS)

    def on_mouse_move(self, x, y):
        pass

    def timer(self, fps):
        glut.glutTimerFunc(1000/fps, self.timer, fps)
        glut.glutPostRedisplay()

    def loop(self):
        glut.glutMainLoop()

    def display(self):
        # clear the buffer
        self.shader.bind()

        gl.glClearColor(0, 0, 0, 0)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)

        try:
            gl.glClearColor(0, 0, 0, 0)
            gl.glClear(gl.GL_COLOR_BUFFER_BIT)

            gl.glBindVertexArray(self.VAO)
            gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.VBO)
            gl.glVertexAttribPointer(0, 2, gl.GL_FLOAT, gl.GL_FALSE, 0, None)

            gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.UVB)
            gl.glVertexAttribPointer(1, 2, gl.GL_FLOAT, gl.GL_FALSE, 0, None)

            gl.glDrawArrays(gl.GL_TRIANGLES, 0, len(self.data))

            gl.glActiveTexture(gl.GL_TEXTURE0)
            gl.glBindTexture(gl.GL_TEXTURE_2D, self.texture)
            # note: use texture numbers
            self.shader['texture_sampler'] = 0

        except Exception as err:
            print err
            exit(1)

        finally:
            gl.glBindVertexArray(0)
            gl.glUseProgram(0)

            gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)
            gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, 0)

            glut.glutSwapBuffers()

    def reshape(self, width, height):
        gl.glViewport(0, 0, width, height)
        self.width = width
        self.height = height

    @staticmethod
    def keyboard(key, *args):
        if key == '\033':
            sys.exit()


if __name__ == '__main__':
    data = np.array([
        [-1, -1],
        [-1, 1],
        [1, 1],

        [1, -1],
        [1, 1],
        [-1, -1],
    ], dtype=np.float32) / 1.5

    GLAPP(data).loop()
