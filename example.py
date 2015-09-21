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
uniform float blue_level;

layout(location = 0) in vec3 position;
out vec4 g_vertex_color;

void main()
{

    gl_Position.xy = position.xy;
    gl_Position.z = 0;
    gl_Position.w = 1;

    g_vertex_color.rg = (position.xy + 1) / 2.;
    g_vertex_color.b = blue_level;
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
    gl_Position.xyz /= 1;
    EmitVertex();
  }
  EndPrimitive();
}
"""


# Geometry shader
LGS = """
#version 330 core
uniform vec3 light_position;

layout(triangles) in;
layout(triangle_strip, max_vertices = 24) out;

in vec4 g_vertex_color[];
out vec4 vertex_color;

void main() {
    int k;
    for (int i=0; i<3; i++){
        k = i<2 ? i+1 : 0;

        gl_Position = gl_in[i].gl_Position;
        vertex_color = vec4(.2, .2, .2, 0);
        EmitVertex();

        gl_Position.xyz =  2 * gl_in[i].gl_Position.xyz - light_position;
        vertex_color = vec4(.2, .2, .2, 0);
        EmitVertex();

        gl_Position = gl_in[k].gl_Position;
        vertex_color = vec4(.2, .2, .2, 0);
        EmitVertex();

        gl_Position.xyz =  2 * gl_in[k].gl_Position.xyz - light_position;
        vertex_color = vec4(.2, .2, .2, 0);
        EmitVertex();
    }
}
"""


# Fragment shader
FS = """
#version 330 core

out vec4 out_color;
in vec4 vertex_color;

void main()
{
    out_color = vertex_color;
    out_color.a = 1;
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

        self.shader_program = ShaderProgram(VS, FS, GS)
        self.lshader_program = ShaderProgram(VS, FS, LGS)

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

        glut.glutTimerFunc(1000/60, self.timer, 60)
        glut.glutMotionFunc(self.on_mouse_move)

    def on_mouse_move(self, x, y):
        gl.glUseProgram(self.lshader_program.program)

        loc = gl.glGetUniformLocation(self.lshader_program.program, 'light_position')
        gl.glUniform3f(
            loc,
            (float(2 * x) / self.width) - 1,
            - (float(2 * y) / self.height) + 1,
            0
        )

    def timer(self, fps):
        glut.glutTimerFunc(1000/fps, self.timer, fps)
        glut.glutPostRedisplay()

    def loop(self):
        gl.glUseProgram(self.shader_program.program)
        loc = gl.glGetUniformLocation(self.shader_program.program, 'blue_level')
        gl.glUniform1f(loc, .10)

        gl.glUseProgram(self.lshader_program.program)
        loc = gl.glGetUniformLocation(self.lshader_program.program, 'blue_level')
        gl.glUniform1f(loc, .80)
        loc = gl.glGetUniformLocation(self.lshader_program.program, 'light_position')
        gl.glUniform3f(loc, 0, -0.30, 0)

        glut.glutMainLoop()

    def display(self):
        # clear the buffer
        gl.glClearColor(255, 255, 255, 0)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)
        gl.glBindVertexArray(self.VAO)

        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.VBO)
        try:
            gl.glVertexAttribPointer(0, 3, gl.GL_FLOAT, gl.GL_FALSE, 0, None)

            gl.glUseProgram(self.lshader_program.program)
            # draw "count" points from the VBO
            gl.glDrawArrays(gl.GL_TRIANGLES, 0, len(self.data))

            gl.glUseProgram(self.shader_program.program)
            # draw "count" points from the VBO
            gl.glDrawArrays(gl.GL_TRIANGLES, 0, len(self.data))

        finally:
            gl.glBindVertexArray(0)
            gl.glUseProgram(0)
            gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)
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
    import sys
    import numpy as np
    data = np.array([
        [-1, -1, 0],
        [-1, 1, 0],
        [1, 1, 0],

        [1, -1, 0],
        [1, 1, 0],
        [-1, -1, 0],

        [-3, -3, 0],
        [-3, -2, 0],
        [-2, -2, 0],

        [-2, -3, 0],
        [-2, -2, 0],
        [-3, -3, 0],

        [3, 3, 0],
        [3, 2, 0],
        [2, 2, 0],

        [2, 3, 0],
        [2, 2, 0],
        [3, 3, 0],

        [-4, 3, 0],
        [-3, 5, 0],
        [-2, 2, 0],

    ], dtype=np.float32) / 7.


    GLAPP(data).loop()
