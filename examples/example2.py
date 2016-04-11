# -*- coding: utf-8 -*-
import numpy as np

from gl2dl.primitives import rect_triangles

from example1 import GLAPP

if __name__ == '__main__':
    data = np.array([], dtype=np.float32)

    number = 10
    size = 10
    skip = 3

    for w in range(1, number * skip, skip):
        for i in range(1, number * skip, skip):
            hole = rect_triangles(
                i * size, w * size,
                i * size + size, w * size + size)

            data = np.append(data, hole)

    GLAPP(data=data).loop()
