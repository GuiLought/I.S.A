import pygame
import constants
from src.character import Character
from pygame import mixer
from utils import carregar_imagem

mixer.init()
pygame.init()

# criar janela
screen = pygame.display.set_mode((constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT))
pygame.display.set_caption("Teste de Tela")

# criar clock para manter taxa de quadros
clock = pygame.time.Clock()

# carregar imagem do player usando a função genérica
player_image = carregar_imagem("personagens", "link-teste.png")

# carregar imagem do background usando a função genérica
background = carregar_imagem("tela_menu", "menu_generico.jpg")

background = pygame.transform.scale(
    background, (constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT)
)

# criar o player
player = Character(
    constants.PLAYER_START_X,
    constants.PLAYER_START_Y,
    constants.PLAYER_SIZE,
    constants.PLAYER_SPEED,
    player_image
)

# definir variáveis de movimento do player
moving_left = False
moving_right = False
moving_up = False
moving_down = False

# loop principal do jogo
run = True
while run:

    # controlar taxa de quadros
    clock.tick(constants.FPS)

    # calcular movimento do player
    dx = 0
    dy = 0

    if moving_right:
        dx = constants.PLAYER_SPEED
    if moving_left:
        dx = -constants.PLAYER_SPEED
    if moving_up:
        dy = -constants.PLAYER_SPEED
    if moving_down:
        dy = constants.PLAYER_SPEED

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

    # desenhar player
    player.draw(screen)

    # atualizar tela
    pygame.display.update()

pygame.quit()