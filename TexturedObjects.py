
from glapp.PyOGLApp import *
from glapp.LoadMesh import *
from glapp.Light import *

# Definimos los shader para los vertices
vertex_shader = r'''
#version 330 core
in vec3 position;
in vec3 vertex_color;
in vec3 vertex_normal;
in vec2 vertex_uv;
uniform mat4 projection_mat;
uniform mat4 model_mat;
uniform mat4 view_mat;
out vec3 color;
out vec3 normal;
out vec3 fragpos;
out vec3 view_pos;
out vec2 UV;
void main()
{
    // Calcula la posición de la vista
    view_pos = vec3(inverse(model_mat) * 
                    vec4(view_mat[3][0], view_mat[3][1], view_mat[3][2],1));
    // Calcula la posición del vértice proyectada en la pantalla
    gl_Position = projection_mat * inverse(view_mat) * model_mat * vec4(position,1);
    // Calcula la normal del vértice en el espacio del modelo
    normal = mat3(transpose(inverse(model_mat))) * vertex_normal;
    // Calcula la posición del fragmento en el espacio del modelo
    fragpos = vec3(model_mat * vec4(position,1));
    // Propaga el color, las coordenadas UV y la normal hacia el fragment shader
    color = vertex_color;
    UV = vertex_uv;
}
'''

# Definimos los shader para los fragmentos
fragment_shader = r'''
#version 330 core
in vec3 color;
in vec3 normal;
in vec3 fragpos;
in vec3 view_pos;
out vec4 frag_color;

in vec2 UV;
uniform sampler2D tex;

struct light
{
    vec3 position;
    vec3 color;
};

# define NUM_LIGHTS 3
uniform light light_data[NUM_LIGHTS];

vec4 Create_Light(vec3 light_pos, vec3 light_color, vec3 normal, vec3 fragpos, vec3 view_dir)
{
    //ambient
    float a_strength = 0.1;
    vec3 ambient = a_strength * light_color;
    
    //diffuse
    vec3 norm = normalize(normal);
    vec3 light_dir = normalize(light_pos - fragpos);
    float diff = max(dot(norm, light_dir), 0);
    vec3 diffuse = diff * light_color;
    
    //specular
    float s_strength = 0.8;
    vec3 reflect_dir = normalize(-light_dir - norm);
    float spec = pow(max(dot(view_dir, reflect_dir), 0), 32);
    vec3 specular = s_strength * spec * light_color;
    
    return vec4(color * (ambient + diffuse + specular), 1);
}

void main()
{
    vec3 view_dir = normalize(view_pos - fragpos);  
    for(int i = 0; i < NUM_LIGHTS; i++)
        frag_color += Create_Light(light_data[i].position, light_data[i].color, normal, fragpos, view_dir);
        
    frag_color = frag_color * texture(tex, UV);
}
'''


# Clase principal para la aplicacion grafica
class TexturedObjects(PyOGLApp):

    def __init__(self):
        super().__init__(300, 20, 1000, 800)
        glEnable(GL_CULL_FACE)

    def initialise(self):
        # Creacion del programa de shaders
        self.program_id = create_program(vertex_shader, fragment_shader)

        # Cargamos del objeto 'letras' utilizando el archivo saludo.obj y una textura dorada
        self.letras = LoadMesh("models/saludo.obj", "images/dorado_letras.jpg", self.program_id,
                               location=pygame.Vector3(0, 0, 0),
                               scale=pygame.Vector3(3, 3, 3))

        # Generamos las estrellas en posiciones aleatorias cada una con texturas doradas
        num_estrellas = 50
        # Lista en la que se almacenaran las 50 estrellas generadas
        self.estrellas = []
        for _ in range(num_estrellas):
            # Generamos angulos aleatorios en radianes
            theta = random.random() * np.pi     # De [0, 180]
            phi = random.random() * 2*np.pi     # De [0, 360]
            # Calculamos las coordenadas de la estrella aleatoria
            x = np.sin(theta)*np.cos(phi) * 9
            y = np.sin(theta)*np.sin(phi) * 9
            z = np.cos(theta) * 9
            # Calculamos el tamaño aleatorio de la estrella ([0, 1] + 0.3) * 0.2 = [0.06, 0.26]
            s = (random.random() + 0.3) * 0.2
            # Cargamos el objeto estrella utilizando el archivo estrella.obj
            moving_estrella = LoadMesh("models/estrella.obj", "images/gold_texture.jpg",
                                       self.program_id,
                                       location=pygame.Vector3(x, y, z),
                                       scale=pygame.Vector3(s, s, s),
                                       move_rotation=Rotation(1, pygame.Vector3(0, 1, 0)))
            # Agregamos la estrella generada a la lista de estrellas anterior
            self.estrellas.append(moving_estrella)

        # Creamos el objeto esfera con una textura de carton
        self.esfera = LoadMesh("models/esfera.obj", "images/carton.jpg", self.program_id,
                               location=pygame.Vector3(0, 0, -10),
                               scale=pygame.Vector3(0.8, 1, 0.8),
                               # Rotacion inicial en el eje y, 0.3 rad
                               move_rotation=Rotation(0.3, pygame.Vector3(0, 1, 0)),
                               # No hay traslacion inicial
                               move_translate=pygame.Vector3(0, 0, 0))

        # Distancia de traslacion
        translation_dist = 0.05
        # Cantidad de movimientos de la esfera
        self.esfera_num_moves = 200
        # Configuracion de los movimientos de la esfera
        self.esfera_moves = [pygame.Vector3(0, translation_dist, 0),
                             pygame.Vector3(0, self.esfera_num_moves*-translation_dist, 0)]
        self.esfera_move = 0

        # Creamos múltiples esferas con diferentes texturas y movimientos aleatorios
        texturas = ["amarillo.jpg", "azul.png",
                    "rojo.jpg", "verde.jpg", "morado.jpg"]
        # Variable para rastrear el indice de la textura actual
        text_num = 0
        # Numero total de esferas a generar
        self.num_esferas = 30
        # Lista vacia para almacenar las esferas generadas
        self.esferas = []
        # Numero de movimientos para cada esfera en el eje x
        self.esferax_num_moves = 350
        # Lista vacia para almacenar los movimientos de las esferas
        self.esferax_moves = []

        for _ in range(self.num_esferas):
            # Generamos angulos aleatorios en radianes
            theta = random.random() * np.pi
            phi = random.random() * 2*np.pi
            # Generamos posiciones aleatorias dentro de una esfera unitaria
            x = np.sin(theta)*np.cos(phi)
            y = np.sin(theta)*np.sin(phi)
            z = np.cos(theta)

            # Si hay mas texturas disponibles, avanzamos a la siguiente textura
            if text_num + 1 < len(texturas):
                text_num += 1
            # Sino volvemos al indice inicial de la lista de texturas
            else:
                text_num = 0

            # Creamos una esfera con una textura especifica, en este caso dependiendo del indice
            # (text_num) de la lista de texturas
            esfera = LoadMesh("models/esfera.obj", "images/"+texturas[text_num],
                              self.program_id,
                              location=pygame.Vector3(0, self.esfera_num_moves*translation_dist, -5),
                              scale=pygame.Vector3(0.2, 0.2, 0.2),
                              move_rotation=Rotation(0, pygame.Vector3(0, 1, 0)),
                              move_translate=pygame.Vector3(0, 0, 0))
            # Agregamos la esfera a la lista de esferas generadas
            self.esferas.append(esfera)
            # Agregamos los movimientos correspondientes en x para esta esfera a la lista de
            # movimientos en x
            self.esferax_moves.append([
                # Agregamos la traslacion
                pygame.Vector3(x*translation_dist, y*translation_dist, z*translation_dist),
                # Agregamos la rotacion
                pygame.Vector3(self.esferax_num_moves*-x*translation_dist,
                               self.esferax_num_moves*-y*translation_dist,
                               self.esferax_num_moves*-z*translation_dist)])
        # Parametros para controlar los movimientos y las acciones de las esferas
        self.esferax_move = 0
        self.esferas_action = False

        # En este apartado crearemos los fuego artificiales, que son un conjunto de esferas de
        # diferentes texturas y movimientos
        self.fireworks = []
        num_fireworks = 7
        texturas = ["amarillo.jpg", "azul.jpg",
                    "rojo.jpg", "verde.jpg", "morado.jpg"]
        # Indice de la textura
        text_num = 0
        # Numeros de esferas de cada fuego artificial
        num_esferas_firework = 30
        self.fireworks_num_moves = 200
        self.fireworks_moves = []

        for _ in range(num_fireworks):
            pos_theta = random.random() * np.pi
            pos_phi = random.random() * 2 * np.pi
            pos_x = np.sin(pos_theta)*np.cos(pos_phi)*11
            pos_y = np.sin(pos_theta)*np.sin(pos_phi)*11
            pos_z = np.cos(pos_theta)*11
            esferas = []
            esferas_moves = []

            for _ in range(num_esferas_firework):
                dir_theta = random.random() * np.pi
                dir_phi = random.random() * 2 * np.pi
                dir_x = np.sin(dir_theta)*np.cos(dir_phi)
                dir_y = np.sin(dir_theta)*np.sin(dir_phi)
                dir_z = np.cos(dir_theta)

                if text_num + 1 < len(texturas):
                    text_num += 1
                else:
                    text_num = 0

                esfera = LoadMesh("models/esfera.obj", "images/"+texturas[text_num], self.program_id,
                                  location=pygame.Vector3(
                    pos_x, pos_y, pos_z),
                    scale=pygame.Vector3(0.2, 0.2, 0.2),
                    move_rotation=Rotation(
                    0, pygame.Vector3(0, 1, 0)),
                    move_translate=pygame.Vector3(0, 0, 0))

                esferas.append(esfera)

                esfera_moves = [pygame.Vector3(dir_x*translation_dist, dir_y*translation_dist, dir_z*translation_dist),
                                pygame.Vector3(self.fireworks_num_moves*-dir_x*translation_dist,
                                               self.fireworks_num_moves*-dir_y*translation_dist,
                                               self.fireworks_num_moves*-dir_z*translation_dist)]

                esferas_moves.append(esfera_moves)

            self.fireworks.append(esferas)

            self.fireworks_moves.append(esferas_moves)

        self.firework_move = 0

        # Cargando el objeto botella
        self.botella = LoadMesh("models/botella2.obj", "images/botella_texture.jpg",
                                self.program_id,
                                location=pygame.Vector3(12, -2, 0),
                                scale=pygame.Vector3(5, 5, 5),
                                move_rotation=Rotation(0.3, pygame.Vector3(0.8, 2, 0)))
        # Cargando el objeto copa
        self.copa = LoadMesh("models/copa.obj", "images/glass_texture.jpg",
                             self.program_id,
                             location=pygame.Vector3(-13, -2, 0),
                             scale=pygame.Vector3(0.5, 0.5, 0.5),
                             move_rotation=Rotation(0.2, pygame.Vector3(0.5, 0.8, 0)))

        # Cargando el objeto globo
        self.globos = LoadMesh("models/globos.obj", "images/dorado_letras.jpg",
                               self.program_id,
                               location=pygame.Vector3(-10, 1, 0),
                               scale=pygame.Vector3(0.6, 0.6, 0.6),
                               move_rotation=Rotation(0.1, pygame.Vector3(0.2, 0.7, 0)))
        # Creamos una fuente de luz
        self.light1 = Light(self.program_id,
                            pygame.Vector3(0, 10, 15),
                            pygame.Vector3(1, 1, 1),
                            1)
        # Creamos una camara
        self.camera = Camera(self.program_id, self.screen_width, self.screen_height)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    def camera_init(self):
        pass

    def display(self):
        # Limpiamos el buffer de color y el buffer de profundidad
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        # Usando el programa de shaders creado
        glUseProgram(self.program_id)
        # Actualizamos las camaras y las luces
        self.camera.update()
        self.light1.update()

        # Dibujando los objetos en la escena
        self.letras.draw()
        self.botella.draw()
        self.copa.draw()
        self.globos.draw()

        # estrellas
        for estrella in self.estrellas:
            estrella.draw()

        # Comprobamos si es que no hay acciones de esferas en curso
        if not self.esferas_action:
            # Si el movimiento de la esfera es menor al límite
            if self.esfera_move < self.esfera_num_moves:
                # Movemos la esfera
                self.esfera.move_translate = self.esfera_moves[0]
                # Incrementamos el contador de movimientos
                self.esfera_move += 1
            else:   # Si excede el limite
                # Cambiamos el movimiento
                self.esfera.move_translate = self.esfera_moves[1]
                # Reiniciamos el contador de movimientos
                self.esfera_move = 0
                # Indicamos que la accion de las esferas estan en curso
                self.esferas_action = True
            # Dibujamos la esfera
            self.esfera.draw()
        # Si hay acciones de esferas en curso
        else:
            # Si el movimiento de las esferas en x es menor al limite
            if self.esferax_move < self.esferax_num_moves:
                for idx, esfera in enumerate(self.esferas):
                    # Movemos las esferas en x
                    esfera.move_translate = self.esferax_moves[idx][0]
                # Incremetamos el contador de movimientos
                self.esferax_move += 1
            else:
                for idx, esfera in enumerate(self.esferas):
                    # Si excede al limite, cambiamos el movimiento
                    esfera.move_translate = self.esferax_moves[idx][1]
                # Reiniciamos el contador de movimientos
                self.esferax_move = 0
                # Indicamos que la accion de las esferas ha terminado
                self.esferas_action = False

            for esfera in self.esferas:
                esfera.draw()

        # fuegos artifiales
        # Comprobamos si hay movimientos de fuegos artificiales
        if self.firework_move < self.fireworks_num_moves:
            for id_firework, firework in enumerate(self.fireworks):
                for id_esfera, esfera in enumerate(firework):
                    # Movemos las esferas
                    esfera.move_translate = self.fireworks_moves[id_firework][id_esfera][0]
            # Incrementamos el contador de movimientos
            self.firework_move += 1
        else:
            for id_firework, firework in enumerate(self.fireworks):
                for id_esfera, esfera in enumerate(firework):
                    # Cambiamos el movimiento
                    esfera.move_translate = self.fireworks_moves[id_firework][id_esfera][1]
            # Reiniciamos el contador de movimientos
            self.firework_move = 0

        for firework in self.fireworks:
            for esfera in firework:
                # Dibujamos las esferas de los fuegos artificiales
                esfera.draw()

# Iniciamos la apliacion
TexturedObjects().mainloop()
