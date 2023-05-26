import pygame
import random
import time
import multiprocessing
import math
# ...

#reset_time = time.time() + 30  # Reiniciar el juego cada 30 segundos
#time_left = 30
#restart_count = 1
max_score = 0
reward_counter = 0
prev_dist = 0
total_movs = 0

# Define some colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
DARK_GREY = (40, 40, 40)

# Set the width and height of the screen [width, height]
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
BLOCK_SIZE = 10

# Initialize Pygame
pygame.init()

# Set the size of the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# Set the title of the window
pygame.display.set_caption("Snake Game")

# Set the font for the score
font = pygame.font.SysFont(None, 25)

# Define the possible actions
ACTIONS = ["left", "right", "up", "down"]



# Define the Snake class
class Snake:
    def __init__(self):
        self.x = SCREEN_WIDTH / 2
        self.y = SCREEN_HEIGHT / 2
        self.dx = BLOCK_SIZE
        self.dy = 0
        self.body = [[self.x, self.y]]
        self.length = 1

    def move(self):
        self.x += self.dx
        self.y += self.dy

        if self.x < 0:
            self.x = SCREEN_WIDTH - BLOCK_SIZE
        elif self.x >= SCREEN_WIDTH:
            self.x = 0

        if self.y < 0:
            self.y = SCREEN_HEIGHT - BLOCK_SIZE
        elif self.y >= SCREEN_HEIGHT:
            self.y = 0

        # Check if the Snake has collided with its own body
        if len(self.body) > 0 and self.body[0] == [self.x, self.y]:
            raise Exception("Game over")

        # Move the rest of the body
        if len(self.body) > 1:
            for i in range(len(self.body) - 1, 0, -1):
                self.body[i] = self.body[i - 1]

        # Move the head of the Snake
        self.body[0] = [self.x, self.y]


    def grow(self):
        # Add a new section to the body of the Snake
        last_section = self.body[-1]
        self.body.append([last_section[0], last_section[1]])

    def draw(self):
        for x, y in self.body:
            pygame.draw.rect(screen, GREEN, [x, y, BLOCK_SIZE, BLOCK_SIZE])

  

# Define the Food class
class Food:
    def __init__(self):
        self.x = random.randrange(0, SCREEN_WIDTH - BLOCK_SIZE, BLOCK_SIZE)
        self.y = random.randrange(0, SCREEN_HEIGHT - BLOCK_SIZE, BLOCK_SIZE)

    def draw(self):
        pygame.draw.rect(screen, RED, [self.x, self.y, BLOCK_SIZE, BLOCK_SIZE])



# Create the Snake and Food objects
snake = Snake()
food = Food()

# Set the initial score
score = 0

# Set the initial game state
game_over = False

# Set the game clock
clock = pygame.time.Clock()

# Define the Q-learning parameters
alpha = 0.5
gamma = 0.95
epsilon = 0.05

# Define the Q-table
q_table = {}

def get_state(snake, food):
    """
    Returns the current state of the game.
    """
    # Check if the snake has any body parts
    if len(snake.body) == 0:
        return None

    # Get the position of the snake's head
    head = snake.body[0]

    # Get the position of the food
    food_pos = (food.x, food.y)

    # Get the direction of the snake
    dx, dy = snake.dx, snake.dy

    # Return the state as a tuple
    return (head, food_pos, dx, dy)

def act(state, q_table, epsilon):
    """
    Returns the action to take for the given state.
    """
    # Convert the state to a tuple
    state_tuple = tuple(tuple(x) if isinstance(x, list) else x for x in state)

    # Choose an action using epsilon-greedy exploration
    if random.uniform(0, 1) < epsilon:
        # Choose a random action
        action = random.choice(ACTIONS)
    else:
        # Choose the action with the highest Q-value
        if state_tuple in q_table:
            action = max(q_table[state_tuple], key=q_table[state_tuple].get)
        else:
            action = random.choice(ACTIONS)

   

    return action

def distance(p1, p2):
    """
    Returns the Euclidean distance between two points.
    """
    x1, y1 = p1
    x2, y2 = p2
    return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

def reward(new_state):
    """
    Returns the reward for the given state.
    """
    global reward_counter
    global prev_dist

    # Check if the snake has eaten the food
    if new_state[0] == new_state[1]:
        reward = 1000
    else:
        # Check if the snake has collided with a wall or with itself
        if new_state[0] in new_state[2:] or new_state[0][0] < 0 or new_state[0][0] >= SCREEN_WIDTH or new_state[0][1] < 0 or new_state[0][1] >= SCREEN_HEIGHT:
            reward = -1000
        else:
            # Calculate the distance to the food
            food_pos = new_state[1]
            dist = distance(new_state[0], food_pos).__floor__()

            # Calculate the reward based on the distance to the food
            if prev_dist is None:
                reward = -dist * 10
            else:
                diff = prev_dist - dist
                reward = diff * 10

            # Update the previous distance
            prev_dist = dist

    # Update the reward counter
    reward_counter += reward

    return reward
    
# Main game loop
while not game_over:
    # Get the current state
    state = get_state(snake, food)

    # Choose an action
    if random.uniform(0, 1) < epsilon:
        action = random.choice(ACTIONS)
    else:
        action = act(q_table, state, epsilon)

    # Take the action
    if action == "left":
        snake.dx = -BLOCK_SIZE
        snake.dy = 0
    elif action == "right":
        snake.dx = BLOCK_SIZE
        snake.dy = 0
    elif action == "up":
        snake.dx = 0
        snake.dy = -BLOCK_SIZE
    elif action == "down":
        snake.dx = 0
        snake.dy = BLOCK_SIZE

    # Move the Snake
    snake.move()
    total_movs += 1


    # Check for collision with Food
    if snake.body[0][0] == food.x and snake.body[0][1] == food.y:
        food = Food()
        snake.grow()
        score += 1

    # Check for collision with Snake body
    for x, y in snake.body[1:]:
        if snake.body[0][0] == x and snake.body[0][1] == y:
            snake = Snake()
            food = Food()
            score = 0

    # Get the new state
    new_state = get_state(snake, food)

    # Update the Q-table
    state_tuple = tuple(tuple(x) if isinstance(x, list) else x for x in state)
    if state_tuple not in q_table:
        state_tuple = tuple(tuple(tuple(x) if isinstance(x, list) else x for x in state))
        q_table[state_tuple] = {action: 0 for action in ACTIONS}

    new_state_tuple = tuple(tuple(x) if isinstance(x, list) else x for x in new_state)
    if new_state_tuple not in q_table:
        new_state_tuple = tuple(tuple(x) if isinstance(x, list) else x for x in new_state)
        q_table[new_state_tuple] = {action: 0 for action in ACTIONS}

    state_tuple = tuple(tuple(x) if isinstance(x, list) else x for x in state)
    new_state = tuple(tuple(x) if isinstance(x, list) else x for x in new_state)

    q_table[state_tuple][action] += alpha * (reward(new_state) + gamma * max(q_table[new_state].values()) - q_table[state_tuple][action])

    # Verificar si ha pasado el tiempo de reinicio
    #if time.time() >= reset_time:
        # Reiniciar el juego y la serpiente
        #snake = Snake()
        #food = Food()
        #score = 0
        #reset_time = time.time() + 30
         # Incrementar el contador de reinicios
        #restart_count += 1

    # Actualizar la puntuación máxima
    if score > max_score:
        max_score = score
       
    # Clear the screen
    screen.fill(DARK_GREY)

    # Draw the Snake and Food
    snake.draw()
    food.draw()

    # Draw the score
    score_text = font.render("Puntos: " + str(score), True, WHITE)
    screen.blit(score_text, [10, 10])

     # Draw the max score
    #max_score_text = font.render("Max score: " + str(max_score), True, WHITE)
    #screen.blit(max_score_text, [10, 70])

    #Draw the total movs
    total_movs_text = font.render("Total movs: " + str(total_movs), True, WHITE)
    screen.blit(total_movs_text, [10, 30])

    # Render the reward counter
    reward_text = font.render(f"Reward: {reward_counter}", True, (255, 255, 255))
    screen.blit(reward_text, (10, 50))


    # Actualizar el tiempo restante
    #time_left = int(reset_time - time.time())

    # Draw the time left
    #time_text = font.render("Time left: " + str(time_left), True, WHITE)
    #screen.blit(time_text, [10, 30])

    # Draw the restart count
    #restart_text = font.render("Generación: " + str(restart_count), True, WHITE)
    #screen.blit(restart_text, [10, 50])

     # Show the chosen action on the screen
    #action_text = font.render(f"Action: {action}", True, (255, 255, 255))
    #screen.blit(action_text, (10, 110))

    # Update the screen
    pygame.display.flip()

    # Set the game clock
    clock.tick(500)


# Quit Pygame
pygame.quit()