import pygame
import constants
import sys


pygame.init()

screen = pygame.display.set_mode((constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT))
pygame.display.set_caption("Teste de Tela")

#player


#definir variáveis de movimento do player
moving_left = False
moving_right = False
moving_up = False
moving_down = False

#criar player
#player = world.player

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    
    # Preencher a tela com uma cor
    screen.fill(constants.BLACK)
    pygame.display.flip()