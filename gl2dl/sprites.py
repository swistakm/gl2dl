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
    TEXTURE_CLASS = Texture

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
            self._texture = self.TEXTURE_CLASS(file_name)
        else:
            self._texture = texture

        self._shader = ShaderProgram(self.vertex_code, self.fragment_code)

        self.data = rect_triangles(
            0, 0, self._texture.width, self._texture.height
        ) - np.array(pivot, dtype=np.float32)
        self.uv_data = rect_triangles(0, 0, 1, 1)

        # each sprite has it's own VAO
        self.VAO = gl.glGenVertexArrays(1)
        gl.glBindVertexArray(self.VAO)

        # two generic vertex attribute arrays - one for VBO and one for UVB
        gl.glEnableVertexAttribArray(0)
        gl.glEnableVertexAttribArray(1)

        self.VBO = gl.glGenBuffers(1)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.VBO)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, self.data.nbytes, self.data, gl.GL_STATIC_DRAW)  # noqa
        gl.glVertexAttribPointer(0, 2, gl.GL_FLOAT, gl.GL_FALSE, 0, None)

        self.UVB = gl.glGenBuffers(1)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.UVB)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, self.uv_data.nbytes, self.uv_data, gl.GL_STATIC_READ)  # noqa
        gl.glVertexAttribPointer(1, 2, gl.GL_FLOAT, gl.GL_FALSE, 0, None)

        # finally unbind VBO
        gl.glBindVertexArray(0)

    def draw(self, x=0, y=0, scale=1.0):
        with self._shader as active:
            active['scale'] = scale
            active['model_view_projection'] = ortho(
                glut.glutGet(glut.GLUT_WINDOW_WIDTH),
                glut.glutGet(glut.GLUT_WINDOW_HEIGHT),
                x, y,
            )

            gl.glBindVertexArray(self.VAO)

            gl.glActiveTexture(gl.GL_TEXTURE0)
            gl.glBindTexture(gl.GL_TEXTURE_2D, self._texture.texture)
            # note: use texture numbers
            active['texture_sampler'] = 0

            gl.glDrawArrays(gl.GL_TRIANGLES, 0, len(self.data))


class StaticAnimationAtlas(Texture):
    def __init__(self, filename, mode="RGBA"):
        super(StaticAnimationAtlas, self).__init__(filename, mode)

    def get_frame_offset(self, frame_index, width, height):
        # note: cap frames for frame index overflow so user can issue
        #       `draw(frame=time())` in animated sprites
        maxframes = int(self.width / width) * int(self.height / width)

        div, mod = divmod(width * (int(frame_index) % maxframes), self.width)
        # note: assume left-to-right top-to-bottom ordering of frames
        # note: image starts in top-left corner
        pixel_y_offset = self.height - div * height
        pixel_x_offset = mod

        return (
            float(pixel_x_offset) / self.width,
            float(pixel_y_offset) / self.height,
        )

    def get_uv_data(self, width, height):
        return rect_triangles(
            0, 0,
            float(width) / self.width, float(height) / self.height
        )



class AnimatedSprite(Sprite):
    fragment_code = """
        #version 330 core

        // Interpolated values from the vertex shaders
        in vec2 UV;

        // Ouput data
        out vec4 color;

        // Values that stay constant for the whole mesh.
        uniform sampler2D texture_sampler;
        uniform vec2 offset;

        void main(){

            // Output color = color of the texture at the specified UV
            color = texture(texture_sampler, UV+offset).rgba;
        }
    """
    TEXTURE_CLASS = StaticAnimationAtlas

    def __init__(self, frame_size, file_name=None, texture=None, pivot=(0, 0)):
        self.frame_size = frame_size
        super(AnimatedSprite, self).__init__(file_name, texture, pivot)

        # todo: consider refactoring so we do not need to redefine buffers
        gl.glBindVertexArray(self.VAO)
        # note: redefine existing UVB buffer but delete it first
        gl.glDeleteBuffers(1, [self.UVB])
        self.UVB = gl.glGenBuffers(1)
        self.uv_data = self._texture.get_uv_data(*frame_size)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.UVB)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, self.uv_data.nbytes, self.uv_data, gl.GL_STATIC_READ)  # noqa
        gl.glVertexAttribPointer(1, 2, gl.GL_FLOAT, gl.GL_FALSE, 0, None)

        gl.glBindVertexArray(0)

    def draw(self, x=0, y=0, scale=1.0, frame=0):
        with self._shader as active:
            active['offset'] = self._texture.get_frame_offset(frame, *self.frame_size)  # noqa

        # fixme: scale, pivot and sprite sizes are taken directly from texture
        # fixme: and this is serious bug
        super(AnimatedSprite, self).draw(x, y)
