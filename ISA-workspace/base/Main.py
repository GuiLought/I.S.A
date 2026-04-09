import pygame
import Constants
from Character import Character
from pygame import mixer

mixer.init()
pygame.init()

# criar janela
screen = pygame.display.set_mode((Constants.SCREEN_WIDTH, Constants.SCREEN_HEIGHT))
pygame.display.set_caption("Teste de Tela")

# criar clock para manter taxa de quadros
clock = pygame.time.Clock()

# carregar imagem do player
player_image = pygame.image.load(
    "base/assets/personagem/link-teste.png"
).convert_alpha()

#carregar imagem m

# opcional: redimensionar imagem
player_image = pygame.transform.scale(player_image, (Constants.SIZE, Constants.SIZE))
background = pygame.image.load("base/assets/tela_menu/menu_generico.jpg").convert_alpha()
background = pygame.transform.scale(background, (Constants.SCREEN_WIDTH, Constants.SCREEN_HEIGHT))
# criar o player
player = Character(100, 100, Constants.SIZE, Constants.SPEED, player_image)

#gui vou trocar o world para background rapidao


# definir variáveis de movimento do player
moving_left = False
moving_right = False
moving_up = False
moving_down = False

# loop principal do jogo
run = True
while run:

    # controlar taxa de quadros
    clock.tick(Constants.FPS)

    # calcular movimento do player
    dx = 0
    dy = 0

    if moving_right:
        dx = Constants.SPEED
    if moving_left:
        dx = -Constants.SPEED
    if moving_up:
        dy = -Constants.SPEED
    if moving_down:
        dy = Constants.SPEED

    # gerenciador de eventos
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

        # tecla pressionada
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                moving_left = True
            if event.key == pygame.K_d:
                moving_right = True
            if event.key == pygame.K_w:
                moving_up = True
            if event.key == pygame.K_s:
                moving_down = True

        # tecla solta
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                moving_left = False
            if event.key == pygame.K_d:
                moving_right = False
            if event.key == pygame.K_w:
                moving_up = False
            if event.key == pygame.K_s:
                moving_down = False

    # mover player
    player.move(dx, dy)

    # limpar tela
    
    screen.blit(background, (0, 0))
    #screen.fill(Constants.PINK)
    
    # desenhar player
    player.draw(screen)

    # atualizar tela
    pygame.display.update()

pygame.quit()
