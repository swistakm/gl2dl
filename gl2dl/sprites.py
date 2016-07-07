# -*- coding: utf-8 -*-
import OpenGL.GL as gl
import OpenGL.GLUT as glut

from PIL import Image
import numpy as np

from .primitives import ortho, rect_triangles
from .shaders import ShaderProgram


class Texture(object):
    def __init__(self, file_name, mode="RGBA"):
        # todo: consider refactoring because it maybe can be moved somwhere
        # todo: else
        self.file_name = file_name
        self.VAO = gl.glGenVertexArrays(1)
        gl.glBindVertexArray(self.VAO)

        self._image = Image.open(file_name)
        # note: different mode will require different argument in glTexImage2D
        image_bytes = self._image.tobytes("raw", mode, 0, -1)

        # GL texture object initialization
        # todo: consolidate contract, consider inheriting from int or GLuint
        # todo: and maybe using __new__ to create new "ints" objects
        # todo: see OpenGL.GL.shaders.ShaderProgram for reference
        self.texture = gl.glGenTextures(1)
        gl.glBindTexture(gl.GL_TEXTURE_2D, self.texture)
        # note: check what it does!
        gl.glPixelStorei(gl.GL_UNPACK_ALIGNMENT, 1)
        # pass image data as pixels
        gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGBA, self.width, self.height, 0, gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, image_bytes)  # noqa
        gl.glTexParameter(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)  # noqa
        gl.glTexParameter(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_NEAREST)  # noqa

        self.uv_data = rect_triangles(0, 0, 1, 1)
        self.UVB = gl.glGenBuffers(1)

        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.UVB)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, self.uv_data.nbytes, self.uv_data, gl.GL_STATIC_READ)  # noqa
        # note: location of buffer?
        gl.glEnableVertexAttribArray(1)

    @property
    def width(self):
        return self._image.size[0]

    @property
    def height(self):
        return self._image.size[1]


class Sprite(object):
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

    def __init__(self, file_name=None, texture=None, pivot=(0, 0)):
        """
        :param texture: Image object
        :param file_name: file_name object
        :param pivot: sprite pivot (x, y) in texture space for scaling and rotation
        :return:
        """
        if texture and file_name:
            raise ValueError(
                "Sprite can be instantiated by either 'texture' or "
                "'file_name' param but not both!"
            )

        if file_name:
            self._texture = Texture(file_name)
        else:
            self._texture = texture

        self._shader = ShaderProgram(self.vertex_code, self.fragment_code)

        self.data = rect_triangles(
            0, 0, self._texture.width, self._texture.height
        ) - np.array(pivot, dtype=np.float32)

        self.VBO = gl.glGenBuffers(1)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.VBO)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, self.data.nbytes, self.data, gl.GL_STATIC_DRAW)  # noqa
        gl.glEnableVertexAttribArray(0)

    def draw(self, x=0, y=0, scale=1.0):
        with self._shader as active:
            active['scale'] = scale
            active['model_view_projection'] = ortho(
                glut.glutGet(glut.GLUT_WINDOW_WIDTH),
                glut.glutGet(glut.GLUT_WINDOW_HEIGHT),
                x, y,
            )

            gl.glBindVertexArray(self._texture.VAO)
            gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.VBO)
            gl.glVertexAttribPointer(0, 2, gl.GL_FLOAT, gl.GL_FALSE, 0, None)

            gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self._texture.UVB)
            gl.glVertexAttribPointer(1, 2, gl.GL_FLOAT, gl.GL_FALSE, 0, None)

            gl.glActiveTexture(gl.GL_TEXTURE0)
            gl.glBindTexture(gl.GL_TEXTURE_2D, self._texture.texture)
            # note: use texture numbers
            active['texture_sampler'] = 0

            gl.glDrawArrays(gl.GL_TRIANGLES, 0, len(self.data))
