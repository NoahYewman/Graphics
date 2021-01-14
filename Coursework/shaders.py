# imports all openGL functions
from OpenGL.GL import *
from OpenGL.GL import shaders
from matutils import *
# we will use numpy to store data in arrays
import numpy as np


class Uniform:
    """
    We create a simple class to handle uniforms, this is not necessary,
    but allow to put all relevant code in one place
    """

    def __init__(self, uniform_name, value=None):
        """
        Initialise the uniform parameter
        :param uniform_name: the name of the uniform, as stated in the GLSL code
        """
        self.name = uniform_name
        self.value = value
        self.location = -1

    def link(self, program):
        """
        This function needs to be called after compiling the GLSL program to fetch the location of the uniform
        in the program from its name
        :param program: the GLSL program where the uniform is used
        """
        self.location = glGetUniformLocation(program=program, name=self.name)
        if self.location == -1:
            print('(E) Warning, no uniform {}'.format(self.name))

    def bind_matrix(self, M=None, number=1, transpose=True):
        """
        Call this before rendering to bind the Python matrix to the GLSL uniform mat4.
        You will need different methods for different types of uniform, but for now this will
        do for the PVM matrix
        :param number: the number of matrices sent, leave that to 1 for now
        :param transpose: Whether the matrix should be transposed
        """
        if M is not None:
            self.value = M
        if self.value.shape[0] == 4 and self.value.shape[1] == 4:
            glUniformMatrix4fv(self.location, number, transpose, self.value)
        elif self.value.shape[0] == 3 and self.value.shape[1] == 3:
            glUniformMatrix3fv(self.location, number, transpose, self.value)
        else:
            print('(E) Error: Trying to bind as uniform a matrix of shape {}'.format(self.value.shape))

    def bind(self, value):
        if value is not None:
            self.value = value

        if isinstance(self.value, int):
            self.bind_int()
        elif isinstance(self.value, float):
            self.bind_float()
        elif isinstance(self.value, np.ndarray):
            if self.value.ndim == 1:
                self.bind_vector()
            elif self.value.ndim == 2:
                self.bind_matrix()
        else:
            print('Wrong value bound: {}'.format(type(self.value)))

    def bind_int(self, value=None):
        if value is not None:
            self.value = value
        glUniform1i(self.location, self.value)

    def bind_float(self, value=None):
        if value is not None:
            self.value = value
        glUniform1f(self.location, self.value)

    def bind_vector(self, value=None):
        if value is not None:
            self.value = value
        if value.shape[0] == 2:
            glUniform2fv(self.location, 1, value)
        elif value.shape[0] == 3:
            glUniform3fv(self.location, 1, value)
        elif value.shape[0] == 4:
            glUniform4fv(self.location, 1, value)
        else:
            print('(E) Error in Uniform.bind_vector(): Vector should be of dimension 2,3 or 4, found {}'.format(
                value.shape[0]))

    def set(self, value):
        """
        function to set the uniform value (could also access it directly, of course)
        """
        self.value = value


class FurShader:
    """
    This is the base class for loading and compiling the GLSL shaders.
    """

    def __init__(self):
        """
        Initialises the shaders
        :param vertex_shader: the name of the file containing the vertex shader GLSL code
        :param fragment_shader: the name of the file containing the fragment shader GLSL code
        """

        print('Creating shader program.')

        # tells the program where to find the shaders.
        vertex_shader = 'shaders/vertex_shader.glsl'
        fragment_shader = 'shaders/fragment_shader.glsl'

        # load the vertex shader GLSL code
        print('Load vertex shader from file: {}'.format(vertex_shader))
        with open(vertex_shader, 'r') as file:
            self.vertex_shader_source = file.read()

        # load the fragment shader GLSL code
        print('Load fragment shader from file: {}'.format(fragment_shader))
        with open(fragment_shader, 'r') as file:
            self.fragment_shader_source = file.read()

        # All of the uniforms which are required for the shaders.
        self.uniforms = {
            'UVScale': Uniform('UVScale'),
            'num_of_layers': Uniform('num_of_layers'),
            'current_layer': Uniform('current_layer'),
            'projection': Uniform('projection'),
            'view': Uniform('view'),
            'model': Uniform('model'),
            'fur_length': Uniform('fur_length'),
            'furFlowOffset': Uniform('furFlowOffset'),
            'textureUnit0': Uniform('textureUnit0'),
            'textureUnit1': Uniform('textureUnit1')
        }

        self.model_program = None

    def compile(self, attributes):
        """
        Call this function to compile the GLSL codes for both shaders.
        :return:
        """
        print('Compiling GLSL shaders....')
        try:
            self.program = glCreateProgram()
            glAttachShader(self.program, shaders.compileShader(self.vertex_shader_source, shaders.GL_VERTEX_SHADER))
            glAttachShader(self.program, shaders.compileShader(self.fragment_shader_source, shaders.GL_FRAGMENT_SHADER))

        except RuntimeError as error_message:
            print('(E) An error occurred while compiling {} shader:\n {}\n... forwarding exception...'.format(self.name,
                                                                                                              error_message)),
            raise error_message

        self.bindAttributes(attributes)

        # Links the program
        glLinkProgram(self.program)

        # tell OpenGL to use this shader program for rendering
        glUseProgram(self.program)

        # link all uniforms
        for uniform in self.uniforms:
            self.uniforms[uniform].link(self.program)

    def bindAttributes(self, attributes):
        # bind all shader attributes to the correct locations in the VAO
        for attrib_name, location in attributes.items():
            glBindAttribLocation(self.program, location, attrib_name)
            print('Binding attribute {} to location {}'.format(attrib_name, location))

    def bind(self, model, M, UVScale, num_of_layers, fur_length, current_layer, furFlowOffset):
        """
        Call this function to enable this GLSL Program (you can have multiple GLSL programs used during rendering!)
        """

        # tell OpenGL to use this shader program for rendering
        glUseProgram(self.program)

        P = model.scene.P
        V = model.scene.camera.V

        # set the uniforms
        self.uniforms['projection'].bind(P)
        self.uniforms['view'].bind(V)
        self.uniforms['model'].bind(M)

        self.uniforms['UVScale'].bind_float(UVScale)
        self.uniforms['num_of_layers'].bind_float(num_of_layers)
        self.uniforms['fur_length'].bind_float(fur_length)
        self.uniforms['current_layer'].bind_float(current_layer)
        self.uniforms['furFlowOffset'].bind_float(furFlowOffset)
        self.uniforms['textureUnit0'].bind(0)
        self.uniforms['textureUnit1'].bind(1)

    def unbind(self):
        glUseProgram(0)
