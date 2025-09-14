import pygame
import sys
screen_width, screen_height = 1408, 704
pygame.init()
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("gg")
running = True
clock = pygame.time.Clock()
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    pygame.display.flip()
    clock.tick(60)
pygame.quit()
sys.exit()
