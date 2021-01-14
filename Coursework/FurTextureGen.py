import random
import numpy as np

from OpenGL.GL import *


'''
This is the function which creates a texture and plots lots of random points on its surface.
Creates the fur effect. 
'''


def createFurTextures(size, num_of_layers, fur_density):

    # Generates an empty dataset
    data = np.empty(shape=size * size * num_of_layers, dtype=GLubyte)

    # Fills the entire dataframe with 0's. This makes it transparent black.
    data.fill(0.0 * 255.0)

    # Randomly selects lots of pixels, as the pixels are put the same across all layers, strands of hair are formed.
    # When combined, the hairs look like fur.
    for layer in range(num_of_layers):
        length = layer / num_of_layers
        length = 1 - length
        i_density = fur_density * length
        for i in range(int(i_density)):
            x_rand = random.randint(0, size - 1)
            y_rand = random.randint(0, size - 1)
            data[size * size * layer + size * y_rand + x_rand] = 1.0 * 255.0

    # This binds the texture, then returns it.
    texID = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texID)
    glTexStorage2D(GL_TEXTURE_2D, 1, GL_RGBA8, size, size)
    glTexSubImage2D(GL_TEXTURE_2D, 0, 0, 0, size, size, GL_RGBA, GL_UNSIGNED_BYTE, data)

    return texID