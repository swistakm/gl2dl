# -*- coding: utf-8 -*-
import OpenGL.GL as gl
import OpenGL.GLUT as glut

from . import blending
from .shaders import ShaderProgram
from .primitives import ortho

import numpy as np


class ShadowMap(object):
    vertex_code = """
    #version 330 core
    layout(location = 0) in vec2 position;

    uniform mat4 model_view_projection;

    void main()
    {
        gl_Position = model_view_projection * vec4(position.xy, 0, 1);
    }
    """

    geometry_code = """
    #version 330 core
    uniform vec2 light_position;
    uniform mat4 model_view_projection;

    layout(triangles) in;
    layout(triangle_strip, max_vertices = 24) out;

    /* extrapolate point on line p1-p2 in distance 'd' from p2 */
    vec2 extrapolate(vec2 p1, vec2 p2, float d) {
        return d * (p2 - p1) / distance(p2, p1) + p2;
    }

    /* mirror 'point' over given symmetry 'center' */
    vec2 mirror(vec2 point, vec2 center) {
        return center - point;
    }


    void main() {
        int k;

        for (int i=0; i<3; i++) {
            // todo: we may be able to reduce number or edges processed
            //       and so reduce number of triangles generated
            k = i<2 ? i+1 : 0;

            gl_Position = gl_in[i].gl_Position;
            EmitVertex();

            // todo: customize extrapolate lengths
            // todo: option to select shadow form (extrapolate/mirror)
            gl_Position.xy = extrapolate(light_position, gl_in[i].gl_Position.xy, 1);
            EmitVertex();

            gl_Position = gl_in[k].gl_Position;
            EmitVertex();

            gl_Position.xy = extrapolate(light_position, gl_in[k].gl_Position.xy, 1);
            EmitVertex();
        }
    }
    """

    fragment_code = """
    #version 330 core

    out lowp vec4 out_color;
    in vec4 vertex_color;

    void main()
    {
        // note: shadows are black with alpha set to 1. We will later probably
        //       use only alpha but shadows are black anyway
        out_color = vec4(1, 1, 1, 1);
    }
    """

    def __init__(self, occluders):
        """
        TODO: allow passing some kind of shared buffer objects to reduce amount
            of buffers since we will have probably more lights and also take
            care of releasing the VBO, VAO
        TODO: customizable shadow map (length, color, etc)
        :param occluders:
        :return:
        """

        self._data = occluders
        self._shader = ShaderProgram(
            self.vertex_code,
            self.fragment_code,
            self.geometry_code,
        )

        self.VAO = gl.glGenVertexArrays(1)
        gl.glBindVertexArray(self.VAO)

        self.VBO = gl.glGenBuffers(1)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.VBO)
        gl.glBufferData(
            gl.GL_ARRAY_BUFFER,
            self._data.nbytes,
            self._data,
            gl.GL_STATIC_DRAW
        )
        gl.glEnableVertexAttribArray(0)

    def draw(self):
        try:
            gl.glBindVertexArray(self.VAO)
            gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.VBO)
            gl.glVertexAttribPointer(0, 2, gl.GL_FLOAT, gl.GL_FALSE, 0, None)

            with self._shader as active:
                model_view_projection = ortho(
                    glut.glutGet(glut.GLUT_WINDOW_WIDTH),
                    glut.glutGet(glut.GLUT_WINDOW_HEIGHT),
                )
                active['model_view_projection'] = model_view_projection

                # note: precalculate position here to avoid doing this for
                #       every vertex
                active['light_position'] = model_view_projection.dot(
                    np.array([self.position[0], self.position[1], 0, 1])
                )

                gl.glDrawArrays(gl.GL_TRIANGLES, 0, len(self._data))

        finally:
            gl.glBindVertexArray(0)
            gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)

    @property
    def position(self):
        return self._position
        # return self._shader['light_position']

    @position.setter
    def position(self, value):
        self._position = value
        # self._shader.bind()
        # self._shader['light_position'] = value


class GLight(object):
    vertex_code = """
        #version 330 core

        layout(location = 0) in vec2 position;

        void main()
        {
            // passthrough vertex shader
            gl_Position = vec4(position, 0, 1);
        }
    """

    fragment_code = """
        #version 330 core
        uniform vec2 light_position;
        uniform lowp vec3 light_color;
        uniform float radius;

        out lowp vec4 out_color;

        void main()
        {
            // note: origin of gl_FragCoord is the lower-left corner
            //       and light_position is described in window space
            float distance = length(light_position - gl_FragCoord.xy);
            float attenuation = radius / pow(distance, 1.25);

            out_color = vec4(
                attenuation,
                attenuation,
                attenuation,
                1
            ) * vec4(light_color, 1);
        }
    """

    def __init__(self, color, position, occluders, radius=100):
        """
        TODO: world coordinates!

        :param color: light color as 3-element iterable
        :param position: position of light in world-space as 2-element iterable
        :param occluders: iterable for occluding traingles
        """
        self._shader = ShaderProgram(self.vertex_code, self.fragment_code)

        self._shadows = ShadowMap(
            occluders
        ) if occluders is not None else None

        self.position = position
        self.color = color
        self.radius = radius

        self.vertices = np.array([
            [-1, -1],
            [-1, 1],
            [1, -1],
            [1, 1],
        ], dtype=np.float32)

        self.VAO = gl.glGenVertexArrays(1)
        gl.glBindVertexArray(self.VAO)

        self.VBO = gl.glGenBuffers(1)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.VBO)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, gl.GL_STATIC_DRAW)
        gl.glEnableVertexAttribArray(0)

    @property
    def color(self):
        return self._shader['light_color']

    @color.setter
    def color(self, value):
        self._shader.bind()
        self._shader['light_color'] = value

    @property
    def position(self):
        return self._shader['light_position']

    @position.setter
    def position(self, value):
        with self._shader as active:
            active['light_position'] = value

        if self._shadows:
            self._shadows.position = value

    @property
    def radius(self):
        return self._shader['radius']

    @radius.setter
    def radius(self, value):
        self._shader.bind()
        self._shader['radius'] = value

    def _cut_shadows(self):
        # note:
        # * blending destination: rendered light
        # * blending source: rendered shadows
        #   (black on black, alpha=1 for shadow polygon)
        with blending.blending_rgba(
                # no color wherever there is shadow polygon
                # 0 + 0
                rgb_mode=blending.Mode.ADD,
                rgb_source=blending.Factor.ZERO,
                rgb_destination=blending.Factor.ZERO,

                # 0 + (inverted shadow alpha) * (light alpha)
                alpha_mode=blending.Mode.ADD,
                alpha_source=blending.Factor.ZERO,
                alpha_destination=blending.Factor.ONE_MINUS_SRC_ALPHA,
        ):
            self._shadows.draw()

    def _draw_light(self):
        try:
            with self._shader:
                self._shader.bind()

                gl.glBindVertexArray(self.VAO)
                gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.VBO)
                gl.glVertexAttribPointer(0, 2, gl.GL_FLOAT, gl.GL_FALSE, 0, None)

                gl.glDrawArrays(gl.GL_TRIANGLE_STRIP, 0, len(self.vertices))

        finally:
            gl.glBindVertexArray(0)
            gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)

    def draw(self, cut_shadows=True):
        self._draw_light()
        if cut_shadows and self._shadows:
            self._cut_shadows()
