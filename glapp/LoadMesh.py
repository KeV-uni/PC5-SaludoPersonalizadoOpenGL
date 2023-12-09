from OpenGL.GL import *
from .Mesh import *
import numpy as np
import pygame
import random
from .Utils import *


class LoadMesh(Mesh):
    def __init__(self, filename, imagefile, program_id, draw_type=GL_TRIANGLES,
                 location=pygame.Vector3(0, 0, 0),
                 rotation=Rotation(0, pygame.Vector3(0, 1, 0)),
                 scale=pygame.Vector3(1, 1, 1),
                 move_rotation=Rotation(0, pygame.Vector3(0, 1, 0)),
                 move_translate=pygame.Vector3(0, 0, 0),
                 move_scale=pygame.Vector3(1, 1, 1)
                 ):
        # Cargamos las coordendas,triangulos, coordenadas UV(coordenadas de textura), indices
        # UV, normales e indices normales
        coordinates, triangles, uvs, uvs_ind, normals, normal_ind = self.load_drawing(filename)
        # Formateo de vertices, normales y coordenadas UV
        vertices = format_vertices(coordinates, triangles)
        vertex_normals = format_vertices(normals, normal_ind)
        vertex_uvs = format_vertices(uvs, uvs_ind)
        colors = []

        # Creamos los colores para los vertices
        for i in range(len(vertices)):
            colors.append(1)
            colors.append(1)
            colors.append(1)
        # Llamada al constructor de la clase Mesh con los parametros dados
        super().__init__(program_id, vertices, imagefile, vertex_normals, vertex_uvs, colors, draw_type, location, rotation, scale,
                         move_rotation=move_rotation,
                         move_translate=move_translate,
                         move_scale=move_scale)

    # Metodo para cargar dibujos desde un archivo obj
    def load_drawing(self, filename):
        vertices = []
        triangles = []
        normals = []
        normal_ind = []
        uvs = []
        uvs_ind = []
        # Mientras el archivo este abierto
        with open(filename) as fp:
            # Leemos linea por linea
            line = fp.readline()
            while line:
                # Si la linea comienza con "v", se interpretan como vertices
                if line[:2] == "v ":
                    vx, vy, vz = [float(value) for value in line[2:].split()]
                    vertices.append((vx, vy, vz))
                # Si la linea comienza con "vn", se interpretan como normales
                if line[:2] == "vn":
                    vx, vy, vz = [float(value) for value in line[3:].split()]
                    normals.append((vx, vy, vz))
                # Si comienza con "vt", se interpretan como coordenadas UV
                if line[:2] == "vt":
                    vx, vy = [float(value) for value in line[3:].split()]
                    uvs.append((vx, vy))
                # Si la linea comuenza con "f", se interppretan como caras triangulares
                if line[:2] == "f ":
                    t1, t2, t3 = [value for value in line[2:].split()]
                    triangles.append([int(value) for value in t1.split('/')][0]-1)
                    triangles.append([int(value) for value in t2.split('/')][0]-1)
                    triangles.append([int(value) for value in t3.split('/')][0]-1)
                    uvs_ind.append([int(value) for value in t1.split('/')][1] - 1)
                    uvs_ind.append([int(value) for value in t2.split('/')][1] - 1)
                    uvs_ind.append([int(value) for value in t3.split('/')][1] - 1)
                    normal_ind.append([int(value) for value in t1.split('/')][2] - 1)
                    normal_ind.append([int(value) for value in t2.split('/')][2] - 1)
                    normal_ind.append([int(value) for value in t3.split('/')][2] - 1)
                line = fp.readline()

        # Devuelve las listas de vertices, traingulos, coordenadas UV, indices UV,
        # normales e indeices normales.
        return vertices, triangles, uvs, uvs_ind, normals, normal_ind

