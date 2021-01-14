import pygame

# import the scene class
from scene import Scene

from blender import load_obj_file

from BaseModel import BaseModel

from shaders import *


class RabbitScene(Scene):
    def __init__(self):
        Scene.__init__(self)

        # Initialising the starting variables
        self.fur_density = 30000
        self.fur_length = 0.1
        self.num_of_layers = 30

        # Loads the object, starts with bunny, can be swapped by pressing 'R' and back to bunny with 'B'
        object_to_view = load_obj_file('models/bunny_world.obj')

        # Creating the object
        self.object_to_view = BaseModel(
            scene=self,
            M=np.matmul(translationMatrix([0, +1, 0]), scaleMatrix([2, 2, 2])),
            mesh=object_to_view[0],
            num_of_layers=self.num_of_layers,
            fur_density=self.fur_density,
        )

    def keyboard(self, event):
        """
        Process additional keyboard events for this demo.
        """
        Scene.keyboard(self, event)

        # Keyboard events to change fur length/fur density
        if event.key == pygame.K_l:
            print('Increasing fur length')
            self.fur_length += 0.05
        elif event.key == pygame.K_k:
            print('Decreasing fur length')
            self.fur_length -= 0.05
        elif event.key == pygame.K_m:
            print('Increasing fur density')
            self.fur_density += 5000
        elif event.key == pygame.K_n:
            print('Decreasing fur density')
            self.fur_density -= 5000

        # changes the model to be a bunny
        elif event.key == pygame.K_b:
            self.switchBunny()

        # changes the model to be a rock
        elif event.key == pygame.K_r:
            self.switchRock()

    # Function which creates a bunny object
    def switchBunny(self):
        object_to_view = load_obj_file('models/bunny_world.obj')
        self.object_to_view = BaseModel(
            scene=self,
            M=np.matmul(translationMatrix([0, +1, 0]), scaleMatrix([2, 2, 2])),
            mesh=object_to_view[0],
            num_of_layers=self.num_of_layers,
            fur_density=self.fur_density,
        )

    # Function which creates a rock object
    def switchRock(self):
        object_to_view = load_obj_file('models/rock.obj')
        self.object_to_view = BaseModel(
            scene=self,
            M=np.matmul(translationMatrix([0, +1, 0]), scaleMatrix([2, 2, 2])),
            mesh=object_to_view[0],
            num_of_layers=self.num_of_layers,
            fur_density=self.fur_density,
        )

    def draw(self):
        """
        Draw all models in the scene
        :return: None
        """

        # first we need to clear the scene, we also clear the depth buffer to handle occlusions
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        self.camera.update()

        # for the bunny (it consists of a single mesh).
        self.object_to_view.draw(self.fur_length, self.fur_density, self.num_of_layers)

        # once we are done drawing, we display the scene
        # Note that here we use double buffering to avoid artefacts:
        # we draw on a different buffer than the one we display,
        # and flip the two buffers once we are done drawing.
        pygame.display.flip()


if __name__ == '__main__':
    # initialises the scene object
    scene = RabbitScene()

    # starts drawing the scene
    scene.run()
