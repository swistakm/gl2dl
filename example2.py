# -*- coding: utf-8 -*-
from functools import partial
import sys
import ctypes
import numpy as np
import OpenGL.GL as gl
import OpenGL.GLUT as glut
import OpenGL.GLU as glu
import OpenGL.arrays.vbo as glvbo

# Vertex shader
from shader import ShaderProgram

VS = """
#version 330 core
// Attribute variable that contains coordinates of the vertices.
layout(location = 0) in vec2 position;

// Main function, which needs to set `gl_Position`.
void main()
{
    // The final position is transformed from a null signal to a sinewave here.
    // We pass the position to gl_Position, by converting it into
    // a 4D vector. The last coordinate should be 0 when rendering 2D figures.
    gl_Position = vec4(position.x, .2 * sin(20 * position.x), 0., 1.);
}
"""

# Fragment shader
FS = """
#version 330 core
// Output variable of the fragment shader, which is a 4D vector containing the
// RGBA components of the pixel color.
out vec4 out_color;

// Main fragment shader function.
void main()
{
    // We simply set the pixel color to yellow.
    out_color = vec4(1., 1., 0., 1.);
}
"""


class GLAPP(object):
    def __init__(self, data):
        glut.glutInit()
        glut.glutInitDisplayMode(
            # note: glut.GLUT_3_2_CORE_PROFILE is for Mac OS X
            glut.GLUT_DOUBLE | glut.GLUT_RGBA | glut.GLUT_3_2_CORE_PROFILE
        )
        glut.glutCreateWindow('Hello world!')
        glut.glutReshapeWindow(512, 512)

        self.shader_program = ShaderProgram(VS, FS)
        self.data = data
        # self.vbo = glvbo.VBO(self.data, target=gl.GL_ELEMENT_ARRAY_BUFFER)

        self.VAO = gl.glGenVertexArrays(1)
        gl.glBindVertexArray(self.VAO)

        glut.glutReshapeFunc(self.reshape)
        glut.glutKeyboardFunc(self.keyboard)
        glut.glutDisplayFunc(self.display)

        self.VBO = gl.glGenBuffers(1)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.VBO)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, data.nbytes, data, gl.GL_STATIC_DRAW)
        gl.glEnableVertexAttribArray(0)
        gl.glVertexAttribPointer(0, 4, gl.GL_FLOAT, gl.GL_FALSE, 0, None)

    def loop(self):
        glut.glutMainLoop()

    def display(self):
        # clear the buffer
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)
        gl.glBindVertexArray(self.VAO)

        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.VBO)
        try:
            gl.glVertexAttribPointer(0, 2, gl.GL_FLOAT, gl.GL_FALSE, 0, None)
            gl.glUseProgram(self.shader_program.program)

            # draw "count" points from the VBO
            gl.glDrawArrays(gl.GL_LINE_STRIP, 0, len(self.data))

        finally:
            gl.glBindVertexArray(0)
            gl.glUseProgram(0)
            gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)
            glut.glutSwapBuffers()

    @staticmethod
    def reshape(width, height):
        gl.glViewport(0, 0, width, height)

    @staticmethod
    def keyboard(key, *args):
        if key == '\033':
            sys.exit()


if __name__ == '__main__':
    import sys
    import numpy as np
    # null signal
    data = np.zeros((10000, 2), dtype=np.float32)
    data[:, 0] = np.linspace(-1., 1., len(data))

    GLAPP(data).loop()
