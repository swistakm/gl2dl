# -*- coding: utf-8 -*-
"""
This example shows that there is need to draw rects in batches!
"""
import random

import OpenGL.GLUT as glut
import OpenGL.GL as gl

from gl2dl.shaders import ShaderProgram
from gl2dl.app import App
from gl2dl.primitives import BaseRect, RectBatch, ortho, rect_triangles
from gl2dl.sprites import Texture
import numpy as np

class GLAPP(App):
    vertex_code = """
        #version 330 core

        // Input vertex data, different for all executions of this shader.
        layout(location = 0) in vec2 vertexPosition;
        layout(location = 1) in vec2 vertexUV;

        uniform float scale;
        uniform mat4 model_view_projection;

        // Output data ; will be interpolated for each fragment.
        out vec2 UV;

        void main(){
            gl_Position =  model_view_projection * vec4(vertexPosition, 0, 1/scale);

            // UV of the vertex. No special space for this one.
            UV = vertexUV;
        }
    """

    fragment_code = """
        #version 330 core

        // Interpolated values from the vertex shaders
        in vec2 UV;

        // Ouput data
        out vec4 color;

        // Values that stay constant for the whole mesh.
        uniform sampler2D texture_sampler;

        void main(){

            // Output color = color of the texture at the specified UV
            color = texture(texture_sampler, UV).rgba;
        }
    """
    def init(self, size, positions):
        self.rect_batch = RectBatch()

        for pos in positions:
            self.rect_batch.append([pos, BaseRect(*size)])

        self.rects = self.rect_batch.get_triangles()

        self.shader = ShaderProgram(self.vertex_code, self.fragment_code)
        self.texture = Texture('assets/testtiles.png')

        self.VBO = gl.glGenBuffers(1)

        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.VBO)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, self.rects.nbytes, self.rects, gl.GL_STATIC_DRAW)  # noqa
        gl.glEnableVertexAttribArray(0)

        self.UVB = gl.glGenBuffers(1)
        # note: each traingle needs it's own UV coordinates
        self.uv_data = np.concatenate([
            rect_triangles(0, 0, 1, 1)
            for _ in positions
        ])

        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.UVB)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, self.uv_data.nbytes, self.uv_data, gl.GL_STATIC_READ)  # noqa

    def display(self):
        try:
            self.clear()

            with self.shader as active:
                active['scale'] = 1
                active['model_view_projection'] = ortho(
                    glut.glutGet(glut.GLUT_WINDOW_WIDTH),
                    glut.glutGet(glut.GLUT_WINDOW_HEIGHT),
                    x, y,
                )

                gl.glBindVertexArray(self.texture.VAO)
                gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.VBO)
                gl.glVertexAttribPointer(0, 2, gl.GL_FLOAT, gl.GL_FALSE, 0, None)

                gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.UVB)
                gl.glVertexAttribPointer(1, 2, gl.GL_FLOAT, gl.GL_FALSE, 0, None)

                gl.glActiveTexture(gl.GL_TEXTURE0)
                gl.glBindTexture(gl.GL_TEXTURE_2D, self.texture.texture)

                self.shader['texture_sampler'] = 0

                gl.glDrawArrays(gl.GL_TRIANGLES, 0, len(self.rects))


        except Exception as err:
            print(err)
            exit(1)


if __name__ == '__main__':
    size = 16*3, 16*3

    positions = [
        (x * random.randint(80, 160), y * random.randint(80, 160))
        for x in range(5)
        for y in range(5)
    ]

    app = GLAPP(size=size, positions=positions)

    app.loop()

