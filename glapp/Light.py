import pygame
from .Transformations import *
from .Uniform import *


class Light:
    # Inicializamos la clase Light con valores predeterminados
    def __init__(self, program_id, position=pygame.Vector3(0, 0, 0), color=pygame.Vector3(1, 1, 1), light_number=0):
        # Establecemos la transformacion como la matriz identidad
        self.transformation = identity_mat()
        # Asigna el ID del programa de shaders
        self.program_id = program_id
        # Asigna la posicion de la luz
        self.position = position
        # Asigna el colo de la luz
        self.color = color
        # Definimos la variables para la posicion y el color de la luz en los shaders
        self.light_variable = "light_data[" + str(light_number) + "].position"
        self.color_variable = "light_data[" + str(light_number) + "].color"

    # Metodo para actualizar la posicion y el colo de la luz en los shaders
    def update(self):
        # Creamos un objeto Uniform para la posicion de luz
        light_pos = Uniform("vec3", self.position)
        # Encuentra la variable de posición en los shaders
        light_pos.find_variable(self.program_id, self.light_variable)
        # Cargamos la posicion de la luz en la variable correspondiente en los shaders
        light_pos.load()
        # Creamos un objeto Uniform para el color de la luz
        color = Uniform("vec3", self.color)
        # Encuentra la variable de color en los shaders
        color.find_variable(self.program_id, self.color_variable)
        # Cargamos el color de la luz en la variable correspondiente en los shaders
        color.load()
