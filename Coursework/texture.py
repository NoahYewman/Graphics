import pygame
from OpenGL.GL import *


class Texture:
    """
    Class to handle texture loading.
    """

    def __init__(self, name, img=None, wrap=GL_REPEAT, sample=GL_NEAREST, format=GL_RGBA, type=GL_UNSIGNED_BYTE,
                 target=GL_TEXTURE_2D):
        self.name = name
        self.format = format
        self.type = type
        self.wrap = wrap
        self.sample = sample
        self.target = target

        self.textureid = glGenTextures(1)

        print('* Loading texture {} at ID {}'.format('./textures/{}'.format(name), self.textureid))

        self.bind()

        if img is None:
            # load the image from file using pyGame - any other image reading function could be used here.
            print('Loading texture: texture/{}'.format(name))
            img = pygame.image.load('./textures/{}'.format(name))

            # convert the python image object to a plain byte array for passing to OpenGL
            data = pygame.image.tostring(img, "RGBA", 1)

            self.height = img.get_height()
            self.width = img.get_width()

            # load the texture in the buffer
            glTexImage2D(self.target, 0, format, self.width, self.height, 0, format, type, data)
        else:
            # if a data array is provided use this
            glTexImage2D(self.target, 0, format, img.shape[0], img.shape[1], 0, format, type, img)

        # set what happens for texture coordinates outside [0,1]
        glTexParameteri(self.target, GL_TEXTURE_WRAP_S, wrap)
        glTexParameteri(self.target, GL_TEXTURE_WRAP_T, wrap)

        # set how sampling from the texture is done.
        glTexParameteri(self.target, GL_TEXTURE_MAG_FILTER, sample)
        glTexParameteri(self.target, GL_TEXTURE_MIN_FILTER, sample)

        self.unbind()

    def bind(self):
        glBindTexture(self.target, self.textureid)

    def unbind(self):
        glBindTexture(self.target, 0)
