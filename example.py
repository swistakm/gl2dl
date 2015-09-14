# -*- coding: utf-8 -*-
from functools import partial
import sys
import ctypes
import numpy as np
import OpenGL.GL as gl
import OpenGL.GLUT as glut
import OpenGL.GLU as glu
import OpenGL.arrays.vbo as glvbo

from shader import ShaderProgram

# Vertex shader
VS = """
#version 330 core

layout(location = 0) in vec3 position;
out vec4 g_vertex_color;

void main()
{
     gl_Position.xy = position.xy;
     gl_Position.z = 0;
     gl_Position.w = 1;

    g_vertex_color.rg = (position.xy + 1.0) / 2.;
    g_vertex_color.b = 0.3;
}
"""

# Geometry shader
GS = """
#version 330 core

layout(triangles) in;
layout(triangle_strip, max_vertices = 3) out;

in vec4 g_vertex_color[];
out vec4 vertex_color;

void main() {
  for(int i = 0; i < 3; i++) { // You used triangles, so it's always 3
    vertex_color = g_vertex_color[i];
    gl_Position = gl_in[i].gl_Position;
    gl_Position.xyz /= 2;
    EmitVertex();
  }
  EndPrimitive();
}
"""

# Fragment shader
FS = """
#version 330 core

out vec4 out_color;
in vec4 vertex_color;

void main()
{
    // out_color.rgb = gl_FragCoord.xzy;
    out_color.a = 120.0001;
    out_color = vertex_color;
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

        self.shader_program = ShaderProgram(VS, FS, GS)
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
            gl.glVertexAttribPointer(0, 3, gl.GL_FLOAT, gl.GL_FALSE, 0, None)
            gl.glUseProgram(self.shader_program.program)

            # draw "count" points from the VBO
            gl.glDrawArrays(gl.GL_TRIANGLES, 0, len(self.data))

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
    data = np.array([
        [-1, -1, 0],
        [0, 1, 0],
        [1, -1, 0],
        ], dtype=np.float32
    )

    GLAPP(data).loop()
