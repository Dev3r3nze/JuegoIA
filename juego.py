import pygame
import random
import numpy as np


# Definir colores
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# Inicializar Pygame
pygame.init()

# Definir el tamaño de la pantalla
size = (500, 500)
screen = pygame.display.set_mode(size)
pygame.display.set_caption("Fruit Eater")

# Definir variables del temporizador
start_time = pygame.time.get_ticks()  # tiempo actual en milisegundos

# Definir variables del juego
done = False
clock = pygame.time.Clock()
fruits = 0

# Definir variables de la serpiente
snake_pos = [250, 250]
snake_body = [[250, 250], [240, 250], [230, 250]]
snake_speed = 10
direction = 'RIGHT'

# Definir variables de la fruta
fruit_pos = [random.randrange(1, 50) * 10, random.randrange(1, 50) * 10]
fruit_spawned = True

# Definir funciones del juego
def draw_snake(snake_body):
    for pos in snake_body:
        pygame.draw.rect(screen, GREEN, pygame.Rect(pos[0], pos[1], 10, 10))

def move_snake(snake_pos, snake_body, direction):
    if direction == 'RIGHT':
        snake_pos[0] += snake_speed
    elif direction == 'LEFT':
        snake_pos[0] -= snake_speed
    elif direction == 'UP':
        snake_pos[1] -= snake_speed
    elif direction == 'DOWN':
        snake_pos[1] += snake_speed

    snake_body.insert(0, list(snake_pos))
    snake_body.pop()

    return snake_body

def spawn_fruit(fruit_pos):
    pygame.draw.rect(screen, RED, pygame.Rect(fruit_pos[0], fruit_pos[1], 10, 10))

# Iniciar bucle principal del juego
while not done:

    # Actualizar el temporizador
    elapsed_time = pygame.time.get_ticks() - start_time
    

    # Manejar eventos del juego
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True

    # Definir dirección de la serpiente
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        direction = 'LEFT'
    elif keys[pygame.K_RIGHT]:
        direction = 'RIGHT'
    elif keys[pygame.K_UP]:
        direction = 'UP'
    elif keys[pygame.K_DOWN]:
        direction = 'DOWN'

    # Mover la serpiente
    snake_body = move_snake(snake_pos, snake_body, direction)

    # Verificar si la serpiente choca con los bordes del juego
    if snake_pos[0] < 0 or snake_pos[0] > size[0] - 10 or snake_pos[1] < 0 or snake_pos[1] > size[1] - 10:
        done = True

    # Verificar si la serpiente choca con su propio cuerpo
    for block in snake_body[1:]:
        if snake_pos[0] == block[0] and snake_pos[1] == block[1]:
            done = True

    # Verificar si la serpiente come una fruta
    if snake_pos[0] == fruit_pos[0] and snake_pos[1] == fruit_pos[1]:
        fruit_spawned = False
        snake_body.append([0, 0])
        fruits += 1

    # Dibujar el fondo
    screen.fill(BLACK)

    # Dibujar la serpiente y la fruta
    draw_snake(snake_body)
    if not fruit_spawned:
        fruit_pos = [random.randrange(1, 50) * 10, random.randrange(1, 50) * 10]
        fruit_spawned = True
    spawn_fruit(fruit_pos)

    # Dibujar el temporizador en la pantalla
    font = pygame.font.Font(None, 16)
    timer_text = font.render(f"Time: {int(elapsed_time/1000)} seconds", True, WHITE)
    screen.blit(timer_text, [10, 10])
    # Dibujar la cantidad de frutas recolectadas en la pantalla
    font = pygame.font.Font(None, 16)
    fruit_text = font.render(f"Fruits: {fruits}", True, WHITE)
    screen.blit(fruit_text, [10, 25])

    # Actualizar la pantalla
    pygame.display.update()

    # Establecer la velocidad del juego
    clock.tick(20)

    def get_state(board, snake, fruit):
        # Creamos una matriz vacía del mismo tamaño que el tablero
        state = np.zeros_like(board)

        # Marcamos la posición de la serpiente con 1 en la capa correspondiente
        for i, (x, y) in enumerate(snake):
            state[0, y, x] = 1 if i == 0 else 0

        # Marcamos la posición de la fruta con 1 en la capa correspondiente
        state[1, fruit[1], fruit[0]] = 1

        # Marcamos las casillas que contienen obstáculos (la serpiente sin contar la cabeza)
        state[2, :, :] = (board == 1) & (state[0, :, :] == 0)

        return state
    
    def get_action(state, model, epsilon):
        # Obtener las predicciones de valor para cada acción
        action_values = model.predict(np.array([state]))
        
        # Elegir la acción con el valor más alto (explotación) o una aleatoria (exploración)
        if np.random.rand() < epsilon:
            action = np.random.randint(0, 4)
        else:
            action = np.argmax(action_values)
        
        return action
    
    def update_state(state, action):
        """
        Función que actualiza el estado del juego después de que el agente haya tomado una acción.
        
        Parámetros:
        - state: el estado actual del juego, representado por una matriz.
        - action: la acción que el agente ha decidido tomar. Es un número entero que indica la dirección
                en la que el agente debe moverse (0=izquierda, 1=arriba, 2=derecha, 3=abajo).
        
        Retorna:
        - El nuevo estado del juego, representado por una matriz.
        """
        # Obtenemos la posición actual de la cabeza de la serpiente
        head_pos = np.argwhere(state == 1)[0]

        # Calculamos la nueva posición de la cabeza de la serpiente en función de la acción tomada
        if action == 0:  # izquierda
            new_head_pos = [head_pos[0], head_pos[1] - 1]
        elif action == 1:  # arriba
            new_head_pos = [head_pos[0] - 1, head_pos[1]]
        elif action == 2:  # derecha
            new_head_pos = [head_pos[0], head_pos[1] + 1]
        elif action == 3:  # abajo
            new_head_pos = [head_pos[0] + 1, head_pos[1]]

        # Comprobamos si la nueva posición de la cabeza está dentro del tablero o no
        if (new_head_pos[0] < 0 or new_head_pos[0] >= size or
            new_head_pos[1] < 0 or new_head_pos[1] >= size):
            # Si la nueva posición está fuera del tablero, la serpiente ha chocado contra la pared
            new_state = None
            reward = -1
            done = True
        elif state[new_head_pos[0], new_head_pos[1]] == 1:
            # Si la nueva posición está ocupada por la serpiente, la serpiente ha chocado contra su propio cuerpo
            new_state = None
            reward = -1
            done = True
        elif state[new_head_pos[0], new_head_pos[1]] == 2:
            # Si la nueva posición está ocupada por una fruta, la serpiente ha comido una fruta
            new_state = np.zeros_like(state)
            new_state[new_head_pos[0], new_head_pos[1]] = 1  # la nueva cabeza de la serpiente
            new_state[state == 1] = 3  # el cuerpo de la serpiente se convierte en la nueva cabeza
            new_state[state == 3] = 1  # el resto del cuerpo sigue siendo cuerpo
            place_fruit(new_state)  # se coloca una nueva fruta en una posición aleatoria
            reward = 1
            done = False
        else:
            # Si la nueva posición está libre, la serpiente simplemente se mueve
            new_state = np.zeros_like(state)
            new_state[new_head_pos[0], new_head_pos[1]] = 1  # la nueva cabeza de la serpiente
            new_state[state == 1] = 3  # el cuerpo de la serpiente se convierte en la nueva cabeza
            new_state[state == 3] = 1  # el resto del cuerpo sigue siendo cuerpo
            reward = 0
            done = False

    def place_fruit(snake):
        while True:
            fruit_pos = [random.randrange(1, 50) * 10, random.randrange(1, 50) * 10]
            if fruit_pos not in snake:
                return fruit_pos


    def get_reward(state, action):
        # Obtener las coordenadas del snake y la posición de la fruta
        snake_head = state['snake'][0]
        fruit_pos = state['fruit']

        # Realizar la acción y actualizar el estado del juego
        new_state = update_state(state, action)

        # Calcular la distancia euclidiana entre la cabeza del snake y la fruta
        distance = np.sqrt((snake_head[0] - fruit_pos[0])**2 + (snake_head[1] - fruit_pos[1])**2)

        # Si el snake ha comido la fruta, otorgar una recompensa de +1
        if new_state['snake'][0] == fruit_pos:
            return 1

        # Si el snake ha perdido el juego, otorgar una recompensa de -1
        if done(new_state):
            return -1

        # Si no ha ocurrido nada especial, devolver una recompensa negativa proporcional a la distancia a la fruta
        return -distance / (state['width'] + state['height'])



#Cerrar el juego
pygame.quit()