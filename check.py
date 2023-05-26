import pygame

pygame.init()

# Set the width and height of the screen
size = (700, 500)
screen = pygame.display.set_mode(size)

pygame.display.set_caption("Pygame Test")

# Loop until the user clicks the close button
done = False

# Used to manage how fast the screen updates
clock = pygame.time.Clock()

# Main game loop
while not done:
    # --- Main event loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True

    # --- Game logic should go here

    # --- Drawing code should go here
    # Clear the screen to white
    screen.fill((255, 255, 255))

    # --- Go ahead and update the screen
    pygame.display.flip()

    # --- Limit to 60 frames per second
    clock.tick(60)

# Close the window and quit.
pygame.quit()