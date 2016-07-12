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
        image_bytes = self._image.convert(mode).tobytes("raw", mode, 0, -1)

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
            self._texture = self._setup_texture(file_name)
        else:
            self._texture = texture

        self.pivot = pivot
        self._shader = ShaderProgram(self.vertex_code, self.fragment_code)

        # each sprite has it's own VAO
        self.VAO = gl.glGenVertexArrays(1)
        gl.glBindVertexArray(self.VAO)

        # two generic vertex attribute arrays - one for VBO and one for UVB
        gl.glEnableVertexAttribArray(0)
        self.VBO = self._setup_vbo(0)

        gl.glEnableVertexAttribArray(1)
        self.UVB = self._setup_uvb(1)

        # finally unbind VBO
        gl.glBindVertexArray(0)

    def _setup_texture(self, file_name):
        return self.TEXTURE_CLASS(file_name)

    def _setup_vbo(self, attribute_index):
        vertices = rect_triangles(
            0, 0, self._texture.width, self._texture.height
        ) - np.array(self.pivot, dtype=np.float32)

        vbo = gl.glGenBuffers(1)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, vertices.nbytes, vertices, gl.GL_STATIC_DRAW)  # noqa
        gl.glVertexAttribPointer(attribute_index, 2, gl.GL_FLOAT, gl.GL_FALSE, 0, None)  # noqa

        return vbo

    def _setup_uvb(self, attribute_index):
        uv_coordinates = rect_triangles(0, 0, 1, 1)

        uvb = gl.glGenBuffers(1)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, uvb)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, uv_coordinates.nbytes, uv_coordinates, gl.GL_STATIC_READ)  # noqa
        gl.glVertexAttribPointer(attribute_index, 2, gl.GL_FLOAT, gl.GL_FALSE, 0, None)  # noqa

        return uvb

    def draw(self, x=0, y=0, scale=1.0, flip_x=False, flip_y=False):
        with self._shader as active:
            active['scale'] = scale
            active['model_view_projection'] = ortho(
                # fixme: pluggable windowing interface or replace with glut
                glut.glutGet(glut.GLUT_WINDOW_WIDTH),
                glut.glutGet(glut.GLUT_WINDOW_HEIGHT),
                x, y,
                flip_x, flip_y
            )

            gl.glBindVertexArray(self.VAO)

            gl.glActiveTexture(gl.GL_TEXTURE0)
            gl.glBindTexture(gl.GL_TEXTURE_2D, self._texture.texture)
            # note: use texture numbers
            active['texture_sampler'] = 0

            # note: sprite polygon has always 6 vertices
            gl.glDrawArrays(gl.GL_TRIANGLES, 0, 6)


class StaticAnimationAtlas(Texture):
    def __init__(self, filename, mode="RGBA", subsheets=None):
        self.subsheets = subsheets
        super(StaticAnimationAtlas, self).__init__(filename, mode)

    def _frame_from_subsheet(self, frame_index, subsheet_name):
        if self.subsheets is None or subsheet_name is None:
            return frame_index

        else:
            subsheet = self.subsheets[subsheet_name]
            return subsheet[0] + (
                int(frame_index) % (subsheet[1] - subsheet[0] + 1)
            )

    def get_frame_offset(self, frame_index, width, height, subsheet=None):
        # note: cap frames for frame index overflow so user can issue
        #       `draw(frame=time())` in animated sprites
        frame_index = self._frame_from_subsheet(frame_index, subsheet)
        maxframes = int(self.width / width) * int(self.height / width)

        div, mod = divmod(width * (int(frame_index) % maxframes), self.width)
        # note: assume left-to-right top-to-bottom ordering of frames
        # note: image starts in top-left corner
        pixel_y_offset = self.height - (div + 1) * height
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

    def __init__(
            self, frame_size,
            file_name=None,
            texture=None,
            pivot=(0, 0),
            subsheets=None,
    ):
        self.frame_size = frame_size
        self.subsheets = subsheets
        super(AnimatedSprite, self).__init__(file_name, texture, pivot)

    def _setup_texture(self, file_name):
        return self.TEXTURE_CLASS(file_name, subsheets=self.subsheets)

    def _setup_vbo(self, attribute_index):
        vertices = rect_triangles(
            0, 0, *self.frame_size
        ) - np.array(self.pivot, dtype=np.float32)

        vbo = gl.glGenBuffers(1)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, vertices.nbytes, vertices, gl.GL_STATIC_DRAW)  # noqa
        gl.glVertexAttribPointer(attribute_index, 2, gl.GL_FLOAT, gl.GL_FALSE, 0, None)  # noqa

    def _setup_uvb(self, attribute_index):
        uvb = gl.glGenBuffers(1)

        uv_coordinates = self._texture.get_uv_data(*self.frame_size)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, uvb)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, uv_coordinates.nbytes, uv_coordinates, gl.GL_STATIC_READ)  # noqa
        gl.glVertexAttribPointer(attribute_index, 2, gl.GL_FLOAT, gl.GL_FALSE, 0, None)  # noqa
        return uvb

    def draw(
            self,
            x=0, y=0,
            scale=1.0,
            frame=0, subsheet=None,
            flip_x=False, flip_y=False
    ):
        with self._shader as active:
            active['offset'] = self._texture.get_frame_offset(
                frame, *self.frame_size, subsheet=subsheet
            )  # noqa

        super(AnimatedSprite, self).draw(x, y, scale, flip_x, flip_y)
