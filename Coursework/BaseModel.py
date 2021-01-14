from mesh import Mesh
from shaders import *
from texture import Texture

from FurTextureGen import createFurTextures
from matutils import poseMatrix
from shaders import FurShader


class BaseModel:
    """
    Base class for all models, implementing the basic draw function for triangular meshes.
    Inherit from this to create new models.
    """

    def __init__(self, scene, num_of_layers, fur_density, M=poseMatrix(), mesh=Mesh(), color=None,
                 primitive=GL_TRIANGLES, visible=True):
        """
        Initialises the model data
        """
        print('+ Initializing {}'.format(self.__class__.__name__))

        # if this flag is set to False, the model is not rendered
        self.visible = visible

        # store the scene reference
        self.scene = scene

        # store the type of primitive to draw
        self.primitive = primitive

        # store the object's color (deprecated now that we have per-vertex colors)
        self.color = color

        # store the shader program for rendering this model
        self.shader = None

        # mesh data
        self.mesh = mesh
        if self.mesh.textures == 1:
            self.mesh.textures.append(Texture('fur.bmp'))

        # dict of VBOs
        self.vbos = {}

        # dict of attributes
        self.attributes = {}

        # store the position of the model in the scene, ...
        self.M = M

        # We use a Vertex Array Object to pack all buffers for rendering in the GPU (see lecture on OpenGL)
        self.vao = glGenVertexArrays(1)

        # this buffer will be used to store indices, if using shared vertex representation
        self.index_buffer = None

        # Initialises the values to be used later
        self.num_of_layers = num_of_layers
        self.fur_density = fur_density

        # Calls the createFurTextures function using the fur_density which was first initialised.
        self.furTex = createFurTextures(size=128, num_of_layers=self.num_of_layers, fur_density=fur_density)

        # and we check which primitives we need to use for drawing
        if self.mesh.faces.shape[1] == 3:
            self.primitive = GL_TRIANGLES

        elif self.mesh.faces.shape[1] == 4:
            self.primitive = GL_QUADS

        self.bind()

    def initialise_vbo(self, vbo_name, data):
        print('Initialising VBO for attribute {}'.format(vbo_name))

        if data is None:
            print('(W) Warning in {}.bind_attribute(): Data array for attribute {} is None!'.format(
                self.__class__.__name__, vbo_name))
            return

        # bind the location of the attribute in the GLSL program to the next index
        # the name of the location must correspond to a 'in' variable in the GLSL vertex shader code
        self.attributes[vbo_name] = len(self.vbos)

        # create a buffer object...
        self.vbos[vbo_name] = glGenBuffers(1)
        # and bind it
        glBindBuffer(GL_ARRAY_BUFFER, self.vbos[vbo_name])

        # enable the attribute
        glEnableVertexAttribArray(self.attributes[vbo_name])

        # Associate the bound buffer to the corresponding input location in the shader
        # Each instance of the vertex shader will get one row of the array
        # so this can be processed in parallel!
        glVertexAttribPointer(index=self.attributes[vbo_name], size=data.shape[1], type=GL_FLOAT, normalized=False,
                              stride=0, pointer=None)

        # ... and we set the data in the buffer as the vertex array
        glBufferData(GL_ARRAY_BUFFER, data, GL_STATIC_DRAW)

    def bind_shader(self):
        """
        If a new shader is bound, we need to re-link it to ensure attributes are correctly linked.
        """
        if self.shader is None:
            self.shader = FurShader()

            # binds all attributes to the shader.
            self.shader.compile(self.attributes)

    def bind(self):
        """
        This method stores the vertex data in a Vertex Buffer Object (VBO) that can be uploaded
        to the GPU at render time.
        """

        # bind the VAO to retrieve all buffers and rendering context
        glBindVertexArray(self.vao)

        if self.mesh.vertices is None:
            print('(W) Warning in {}.bind(): No vertex array!'.format(self.__class__.__name__))

        # initialise vertex position VBO and link to shader program attribute
        self.initialise_vbo('position', self.mesh.vertices)
        self.initialise_vbo('normal', self.mesh.normals)
        self.initialise_vbo('texCoord', self.mesh.textureCoords)

        # if indices are provided, put them in a buffer too
        if self.mesh.faces is not None:
            self.index_buffer = glGenBuffers(1)
            glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.index_buffer)
            glBufferData(GL_ELEMENT_ARRAY_BUFFER, self.mesh.faces, GL_STATIC_DRAW)

        # finally we unbind the VAO and VBO when we're done to avoid side effects
        glBindVertexArray(0)
        glBindBuffer(GL_ARRAY_BUFFER, 0)

    def draw(self, fur_length, fur_density, num_of_layers, Mp=poseMatrix()):
        """
        Draws the model using OpenGL functions.
        :param Mp: The model matrix of the parent object, for composite objects.
        """
        if self.visible:

            if self.mesh.vertices is None:
                print('(W) Warning in {}.draw(): No vertex array!'.format(self.__class__.__name__))

            # bind the Vertex Array Object so that all buffers are bound correctly and following operations affect them
            glBindVertexArray(self.vao)

            # Finds whether the current fur density on the model is the same as what it should be,
            # if they are not the same, a new createFurTextures is called, so the updated texture is then shown.
            if self.fur_density != fur_density:
                self.furTex = createFurTextures(size=128, num_of_layers=num_of_layers, fur_density=fur_density)
                self.fur_density = fur_density

            if self.shader is None:
                self.shader = FurShader()
                self.shader.compile(self.attributes)

            # This activates and binds TEXTURE1, which is the skin
            if len(self.mesh.textures) > 0:
                tex = self.mesh.textures[0]
                glActiveTexture(GL_TEXTURE1)
                tex.bind()

            # This activates and binds TEXTURE0, which is generated within furTex, which is generated from the
            # createFurTextures function within the FurTextureGen.py file.
            glActiveTexture(GL_TEXTURE0)
            glBindTexture(GL_TEXTURE_2D, self.furTex)

            # This loops through the layers to draw them all, this means that the fur is generated.
            num = 1
            for current_layer in range(self.num_of_layers):
                num -= 1 // self.num_of_layers
                if num > 1:
                    num = 1
                if num < 0:
                    num = 0

                # This binds the vertex data from the VBO shader.
                # It essentially just gives the shader the information that it needs to work.
                self.shader.bind(
                    model=self,
                    M=np.matmul(Mp, self.M),
                    current_layer=current_layer,
                    UVScale=num,
                    furFlowOffset=0,
                    num_of_layers=num_of_layers,
                    fur_length=fur_length
                )

                if self.mesh.faces is not None:
                    # draw the data in the buffer using the index array
                    glDrawElements(self.primitive, self.mesh.faces.flatten().shape[0], GL_UNSIGNED_INT, None)
                else:
                    # draw the data in the buffer using the vertex array ordering only.
                    glDrawArrays(self.primitive, 0, self.mesh.vertices.shape[0])

            glBindVertexArray(0)

    def __del__(self):
        """
        Release all VBO objects when finished.
        """
        for vbo in self.vbos.values():
            glDeleteBuffers(1, int(vbo))

        glDeleteVertexArrays(1, int(self.vao))
