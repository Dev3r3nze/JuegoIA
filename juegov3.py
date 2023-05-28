import pygame
import random
import math
import itertools

# Inicialización de Pygame
pygame.init()

# Dimensiones de la ventana del juego
width = 800
height = 600

# Colores
black = (0, 0, 0)
white = (255, 255, 255)
yellow = (255, 255, 0)

# Creación de la ventana del juego
window = pygame.display.set_mode((width, height))
pygame.display.set_caption("Juego de Captura de Monedas")

# Carga de la fuente
font = pygame.font.Font(None, 36)

# Clase para representar al jugador
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface([50, 50])
        self.image.fill(yellow)
        self.rect = self.image.get_rect()
    
    def update(self):
        # Obtener la entrada del jugador
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            if self.rect.x > 0:
                self.rect.x -= 5
        if keys[pygame.K_RIGHT]:
            if self.rect.x < width - self.rect.width:
                self.rect.x += 5
        if keys[pygame.K_UP]:
            if self.rect.y > 0:
                self.rect.y -= 5
        if keys[pygame.K_DOWN]:
            if self.rect.y < height - self.rect.height:
                self.rect.y += 5

# Clase para representar las monedas
# Clase para representar las monedas
class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface([30, 30])
        self.image.fill(white)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

# Creación de las monedas con posiciones predefinidas
coin_start_positions = [(100, 100), (200, 200), (300, 300), (400, 400), (500, 500),
                  (600, 100), (700, 200), (100, 300), (200, 400), (300, 500)]
coin_positions = coin_start_positions.copy()

# Creación de los grupos de sprites
all_sprites = pygame.sprite.Group()
coins = pygame.sprite.Group()

for position in coin_start_positions:
    coin = Coin(position[0], position[1])
    all_sprites.add(coin)
    coins.add(coin)




# Creación del jugador
player = Player()
all_sprites.add(player)

def reset_game():
    global collected_coins, start_time, all_sprites, coins, player
    
    all_sprites.empty()
    coins.empty()
    
    player = Player()
    all_sprites.add(player)
    
    for position in coin_positions:
        coin = Coin(position[0], position[1])
        all_sprites.add(coin)
        coins.add(coin)
    
    start_time = pygame.time.get_ticks() // 1
    collected_coins = 0

# Definir las recompensas y penalizaciones
REWARD_COIN = 10
REWARD_CLOSEST_COIN = 1
REWARD_FASTEST_TIME = 5
REWARD_ALL_COINS = 50
REWARD_TIME_REMAINING = 1
PENALTY_HIT_WALL = -5
PENALTY_SLOW_TIME = -10
PENALTY_INEFFICIENT_MOVE = -1
EPSILON = 0.1
ALPHA = 0.1
GAMMA = 0.9
# Definir los estados posibles
print("definir estados posibles")

STATES = []
# Limitar el número máximo de monedas en el juego
MAX_COINS = 5

# Generar combinaciones de posiciones de monedas para el número máximo de monedas
coin_positions_combinations = itertools.combinations(coin_positions, MAX_COINS)

# Generar estados para cada combinación de posiciones de monedas
for x in range(width):
    for y in range(height):
        for coin_positions_combination in coin_positions_combinations:
            coin_positions_combination = list(coin_positions_combination)
            coin_positions_combination.sort()
            coin_positions_binary = [1 if coin in coin_positions_combination else 0 for coin in coin_positions]
            state = (x, y) + tuple(coin_positions_binary)
            STATES.append(state)

# Definir las acciones posibles
ACTIONS = ['left', 'right', 'up', 'down']
# Inicializar la función Q con valores predeterminados
Q_VALUES = {}
for state in STATES:
    for action in ACTIONS:
        Q_VALUES[(state, action)] = 0



# Función para obtener el valor Q para un estado y una acción
def get_q_value(state, action):
    if (state, action) not in Q_VALUES:
        # Inicializar el valor Q en 0 si no se ha visto antes este estado y acción
        Q_VALUES[(state, action)] = 0
    return Q_VALUES[(state, action)]

# Función para actualizar la función Q
def update_q(previous_state, action, current_state, reward):
    # Obtener el valor Q para el estado anterior y la acción tomada
    q_value = get_q_value(previous_state, action)

    # Calcular el nuevo valor Q usando la ecuación de Bellman
    max_q_value = max([get_q_value(current_state, a) for a in ACTIONS])
    new_q_value = q_value + ALPHA * (reward + GAMMA * max_q_value - q_value)

    # Actualizar el valor Q para el estado anterior y la acción tomada
    Q_VALUES[(previous_state, action)] = new_q_value

# Función para obtener la moneda más cercana
def get_closest_coin(player_position, coin_positions):
    closest_coin = None
    closest_distance = 1000000
    for coin_position in coin_positions:
        distance = math.sqrt((player_position[0] - coin_position[0]) ** 2 + (player_position[1] - coin_position[1]) ** 2)
        if closest_coin is None or distance < closest_distance:
            closest_coin = coin_position
            closest_distance = distance
    return closest_coin

# Función para elegir una acción usando Q-learning
def choose_action(state):
    if random.random() < EPSILON:
        # Elegir una acción aleatoria
        return random.choice(ACTIONS)
    else:
        # Elegir la mejor acción según la función Q
        q_values = [get_q_value(state, action) for action in ACTIONS]
        max_q_value = max(q_values)
        if q_values.count(max_q_value) > 1:
            # Si hay varias acciones con el mismo valor Q máximo, elegir una al azar
            best_actions = [i for i in range(len(ACTIONS)) if q_values[i] == max_q_value]
            return ACTIONS[random.choice(best_actions)]
        else:
            return ACTIONS[q_values.index(max_q_value)]
        
# Función de recompensa
def get_reward(previous_state, action, current_state, elapsed_time, collected_coins):
    reward = 0
    # Recompensas
    if collected_coins > previous_state[0]:
        reward += REWARD_COIN
    if current_state[1] in coin_positions:
        reward += REWARD_CLOSEST_COIN
    if elapsed_time < previous_state[2]:
        reward += REWARD_FASTEST_TIME
    if collected_coins == 10:
        reward += REWARD_ALL_COINS
        reward += REWARD_TIME_REMAINING * (10000 - elapsed_time)
    
    # Penalizaciones
    if current_state[3] != previous_state[3]:
        reward += PENALTY_HIT_WALL
    if elapsed_time > previous_state[2]:
        reward += PENALTY_SLOW_TIME
    if action == previous_state[4]:
        reward += PENALTY_INEFFICIENT_MOVE
    
    return reward

# Ciclo principal del juego
running = True
clock = pygame.time.Clock()
start_time = pygame.time.get_ticks() // 1
collected_coins = 0
fastest_time = None
previous_state = (0, 0, 0, False, None)

while running:

    # Verificar si el jugador capturó una moneda
    collected_coins += len(pygame.sprite.spritecollide(player, coins, True))

    # Verificar si el jugador chocó con el límite de la pantalla
    hit_wall = player.rect.left < 0 or player.rect.right > width or player.rect.top < 0 or player.rect.bottom > height

    # Obtener el estado actual del juego
    player_position = (player.rect.x, player.rect.y)
    closest_coin = get_closest_coin(player_position, coin_positions)
    elapsed_time = pygame.time.get_ticks() // 1 - start_time
    all_coins_collected = collected_coins == 10
    current_state = (collected_coins, closest_coin, elapsed_time, hit_wall, None)

    # Elegir una acción usando Q-learning
    action = choose_action(current_state)

    # Realizar la acción elegida
    if action == "left":
        if player.rect.x > 0:
            player.rect.x -= 5
    elif action == "right":
        if player.rect.x < width:
            player.rect.x += 5
    elif action == "up":
        if player.rect.y > 0:
            player.rect.y -= 5
    elif action == "down":
        if player.rect.y < height:
            player.rect.y += 5


   
    # Actualizar la función Q
    if previous_state != (0, 0, 0, False, None):
        reward = get_reward(previous_state, action, current_state, elapsed_time, collected_coins)
        update_q(previous_state, action, current_state, reward)

    # Verificar si el juego ha terminado
    if all_coins_collected or elapsed_time > 10000:
        if all_coins_collected:
            if fastest_time is None or elapsed_time < fastest_time:
                fastest_time = elapsed_time
                print(f"¡Nuevo récord! {fastest_time} s")
        print(f"Monedas: {collected_coins} Tiempo: {elapsed_time} s")    
        previous_state = (collected_coins, closest_coin, elapsed_time, hit_wall, action)
        reset_game()
        continue

    # Dibujar el fondo y los sprites en la ventana
    window.fill(black)
    all_sprites.draw(window)

    # Mostrar el tiempo transcurrido
    time_surface = font.render(f"Tiempo: {elapsed_time} s", True, white)
    window.blit(time_surface, (10, 10))

    # Mostrar el tiempo más rápido obtenido
    if fastest_time is not None:
        fastest_time_surface = font.render(f"Récord: {fastest_time} s", True, white)
        window.blit(fastest_time_surface, (10, 50))

    # Actualizar la pantalla
    pygame.display.flip()

# Finalizar Pygame
pygame.quit()