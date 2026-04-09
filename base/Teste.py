import pygame
import Constants
import sys
from Character import Character
from World import World
from pygame import mixer

mixer.init()
pygame.init()

screen = pygame.display.set_mode((Constants.SCREEN_WIDTH, Constants.SCREEN_HEIGHT))
pygame.display.set_caption("Teste de Tela")

#criar clock para manter taxa de quadros
clock = pygame.time.Clock()

#player
player = Character(100, 100)

#carregar imagem do player
img = pygame.image.load("base/assets/personagem/link-teste.png").convert_alpha()
img = pygame.transform.scale(img, (64, 64))


#definir variáveis de movimento do player
moving_left = False
moving_right = False
moving_up = False
moving_down = False

#criar player


#player = world.player

#loop principal do jogo
run = True
while run:
    # controlar taxa de quadros
    clock.tick(Constants.FPS)

    # gerenciador de eventos
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                moving_left = True
            elif event.key == pygame.K_d:
                moving_right = True
            elif event.key == pygame.K_w:
                moving_up = True
            elif event.key == pygame.K_s:
                moving_down = True
            elif event.key == pygame.K_ESCAPE:
                run = False
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                moving_left = False
            elif event.key == pygame.K_d:
                moving_right = False
            elif event.key == pygame.K_w:
                moving_up = False
            elif event.key == pygame.K_s:
                moving_down = False

    # mover player baseado nas flags
    dx, dy = 0, 0
    speed = 3
    if moving_left:
        dx -= speed
    if moving_right:
        dx += speed
    if moving_up:
        dy -= speed
    if moving_down:
        dy += speed
    player.move(dx, dy)

    # desenhar fundo e player
    screen.fill(Constants.BLACK)
    player.draw(screen)
    # se quiser usar sprite:
    # screen.blit(img, player.rect)

    pygame.display.flip()

pygame.quit()    