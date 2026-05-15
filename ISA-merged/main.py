import pygame
import pandas as pd
import sys
import constants
from src.character import Character
from src.buttons import Botao, BotaoConfig, BotaoSair
from src.world import World
from src.enemies.enemy import Enemy
from src.configuracoes import MenuConfiguracoes
from src.creditos import TelaCreditos
from pygame import mixer
from src.itens.minerio_cobre import minerio_cobre
from utils import carregar_imagem, carregar_tile, carregar_fonte, carregar_nivel_csv, carregar_perguntas_csv

# ── Inicialização ─────────────────────────────────────────────────────────────
mixer.init()
pygame.init()

screen = pygame.display.set_mode((constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT))
pygame.display.set_caption("I.S.A - Projeto QA")
clock = pygame.time.Clock()

# ── Estados possíveis ─────────────────────────────────────────────────────────
# "MENU" | "JOGANDO" | "PAUSADO" | "GAME_OVER" | "QUIZ" | "CONFIGURACOES" | "CREDITOS"
estado_jogo = "MENU"

# ── Recursos permanentes (carregados uma vez) ─────────────────────────────────
background_img = carregar_imagem(
    "tela_menu", "Tela_Menu_Principal.jpg", (constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT)
)
fonte_ui     = carregar_fonte("upheavtt.ttf", 28)
fonte_titulo = carregar_fonte("upheavtt.ttf", 18)

# ── Paralaxe (fundo do modo de jogo) ─────────────────────────────────────────
def _carregar_paralaxe_img(nome):
    img = carregar_imagem("backgrounds", nome)
    return pygame.transform.scale(img, (img.get_width(), constants.SCREEN_HEIGHT))

paralaxe_c1 = _carregar_paralaxe_img("C1.png")
paralaxe_c2 = _carregar_paralaxe_img("C2.png")
VEL_C1    = 4
VEL_C2    = 1
offset_c1 = 0
offset_c2 = 0

def desenhar_paralaxe(dx=0):
    global offset_c1, offset_c2

    if dx != 0:
        offset_c1 -= VEL_C1 if dx > 0 else -VEL_C1
        offset_c2 -= VEL_C2 if dx > 0 else -VEL_C2

    screen.fill((0, 0, 0))

    larg_c2 = paralaxe_c2.get_width()
    off_c2  = offset_c2 % larg_c2
    for x in range(-larg_c2, constants.SCREEN_WIDTH, larg_c2):
        screen.blit(paralaxe_c2, (x + off_c2, 0))

    larg_c1 = paralaxe_c1.get_width()
    off_c1  = offset_c1 % larg_c1
    for x in range(-larg_c1, constants.SCREEN_WIDTH, larg_c1):
        screen.blit(paralaxe_c1, (x + off_c1, 0))

# ── Variáveis de jogo ─────────────────────────────────────────────────────────
player   = None
world    = None
enemies  = []
itens    = []
camera_x = 0
camera_y = 0
moving_left = moving_right = False
jump_pressed = False
perguntas = []
pontuacao = 0
indice = 0
quiz_mensagem = ""
quiz_timer = 0
item_para_remover = None  # Para rastrear qual item remover após o quiz

# ── Carregamento das perguntas ────────────────────────────────────────────────
perguntas = carregar_perguntas_csv("perguntas.csv")

# ── Carregamento do nível ─────────────────────────────────────────────────────
def carregar_recursos_jogo():
    global player, world, enemies, itens, camera_x, camera_y
    global moving_left, moving_right, jump_pressed, pontuacao, indice, quiz_mensagem, quiz_timer, item_para_remover

    tile_surface = carregar_tile("tile_brick.png", constants.TILE_SIZE)
    tile_list    = [tile_surface] * constants.TILE_TYPES

    world_data = carregar_nivel_csv("level1_data.csv")

    world = World()
    world.process_data(world_data, tile_list)
    
    # Sprite inimigo
    
    enemies_image = carregar_imagem("personagens","tronco 2.png")
    enemies_image = pygame.transform.scale(enemies_image, (constants.TILE_SIZE, constants.TILE_SIZE))
    
    
    # Sprite Player
    player_image = carregar_imagem("personagens", "link-teste.png")
    player = Character(
        constants.PLAYER_START_X,
        constants.PLAYER_START_Y,
        constants.PLAYER_SIZE,
        constants.PLAYER_SPEED,
        player_image,
        constants.PLAYER_HEALTH,
    )

    enemies = [
        Enemy(
            x=constants.PLAYER_START_X + 300,
            y=constants.PLAYER_START_Y,
            image=enemies_image,
        )
    ]

    itens = [
        minerio_cobre("m_minerio.png", x=600, y=constants.PLAYER_START_Y, tamanho=(40, 40)),
        minerio_cobre("m_minerio.png", x=900, y=constants.PLAYER_START_Y, tamanho=(40, 40)),
    ]

    camera_x = camera_y = 0
    moving_left = moving_right = jump_pressed = False
    pontuacao = 0
    indice = 0
    quiz_mensagem = ""
    quiz_timer = 0
    item_para_remover = None

# ── Câmera ────────────────────────────────────────────────────────────────────
def atualizar_camera():
    global camera_x, camera_y

    target_x = player.rect.centerx - constants.SCREEN_WIDTH  // 2
    target_y = player.rect.centery - constants.SCREEN_HEIGHT // 2

    map_w = constants.MAP_COLS * constants.TILE_SIZE
    map_h = constants.MAP_ROWS * constants.TILE_SIZE

    camera_x = max(0, min(target_x, map_w - constants.SCREEN_WIDTH))
    camera_y = max(0, min(target_y, map_h - constants.SCREEN_HEIGHT))

# ── Perguntas ─────────────────────────────────────────────────────────────────
def desenhar_pergunta(pergunta):
    screen.fill((0, 0, 0))  # CORRIGIDO: adicionados parênteses extras

    textos = [
        pergunta["pergunta"],
        "A) " + pergunta["opcao_a"],
        "B) " + pergunta["opcao_b"],
        "C) " + pergunta["opcao_c"],
        "D) " + pergunta["opcao_d"],
        "E) " + pergunta["opcao_e"],
    ]

    y = 100
    for texto in textos:  # CORRIGIDO: variável renomeada para não conflitar
        render = fonte_ui.render(texto, True, constants.WHITE)
        screen.blit(render, (50, y))
        y += 50

# ── Debug grid ────────────────────────────────────────────────────────────────
def draw_grid():
    for x in range(constants.SCREEN_WIDTH // constants.TILE_SIZE + 1):
        pygame.draw.line(
            screen, constants.WHITE,
            (x * constants.TILE_SIZE - camera_x % constants.TILE_SIZE, 0),
            (x * constants.TILE_SIZE - camera_x % constants.TILE_SIZE, constants.SCREEN_HEIGHT),
        )
    for y in range(constants.SCREEN_HEIGHT // constants.TILE_SIZE + 1):
        pygame.draw.line(
            screen, constants.WHITE,
            (0, y * constants.TILE_SIZE - camera_y % constants.TILE_SIZE),
            (constants.SCREEN_WIDTH, y * constants.TILE_SIZE - camera_y % constants.TILE_SIZE),
        )


# ── Overlay de texto centralizado ─────────────────────────────────────────────
def draw_overlay_texto(linhas, fonte=None):
    if fonte is None:
        fonte = fonte_ui

    overlay = pygame.Surface(
        (constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT), pygame.SRCALPHA
    )
    overlay.fill((0, 0, 0, 160))
    screen.blit(overlay, (0, 0))

    total_h = len(linhas) * 50
    start_y = (constants.SCREEN_HEIGHT - total_h) // 2
    for i, (texto, cor) in enumerate(linhas):
        surf = fonte.render(texto, True, cor)
        rect = surf.get_rect(center=(constants.SCREEN_WIDTH // 2, start_y + i * 50))
        screen.blit(surf, rect)


# ── Ações dos botões ──────────────────────────────────────────────────────────
def iniciar_jogo():
    global estado_jogo
    carregar_recursos_jogo()
    estado_jogo = "JOGANDO"


def encerrar_jogo():
    pygame.quit()
    sys.exit()


def configurar_jogo():
    global estado_jogo
    estado_jogo = "CONFIGURACOES"


def retomar_jogo():
    global estado_jogo
    estado_jogo = "JOGANDO"


def voltar_menu():
    global estado_jogo, player, world, enemies
    player = world = None
    enemies = []
    estado_jogo = "MENU"


def abrir_creditos():
    global estado_jogo
    estado_jogo = "CREDITOS"


# ── Botões ────────────────────────────────────────────────────────────────────
x_central = (constants.SCREEN_WIDTH // 2) - (constants.BTN_LARGURA // 2)

botoes_menu = [
    Botao("JOGAR", 300, 500, constants.BTN_LARGURA, constants.BTN_ALTURA, iniciar_jogo),
    BotaoSair(cx=700, cy=38, raio=30, acao=encerrar_jogo),
    BotaoConfig(cx=762, cy=38, raio=30, acao=configurar_jogo),
]

botoes_pausa = [
    Botao("RETOMAR", x_central, 220, constants.BTN_LARGURA, constants.BTN_ALTURA, retomar_jogo),
    Botao("MENU",    x_central, 310, constants.BTN_LARGURA, constants.BTN_ALTURA, voltar_menu),
]

botoes_game_over = [
    Botao("REINICIAR", x_central, 280, constants.BTN_LARGURA, constants.BTN_ALTURA, iniciar_jogo),
    Botao("MENU",      x_central, 360, constants.BTN_LARGURA, constants.BTN_ALTURA, voltar_menu),
]

# ── Menu de Configurações e Créditos ─────────────────────────────────────────
menu_cfg = MenuConfiguracoes(
    screen,
    constants.SCREEN_WIDTH,
    constants.SCREEN_HEIGHT,
    callback_voltar=voltar_menu,
    callback_creditos=abrir_creditos,
)

tela_creditos = TelaCreditos(
    screen,
    constants.SCREEN_WIDTH,
    constants.SCREEN_HEIGHT,
    callback_voltar=voltar_menu,
)

# ── Loop principal ────────────────────────────────────────────────────────────
run = True
while run:
    clock.tick(constants.FPS)
    mouse_pos = pygame.mouse.get_pos()

    # Atualizar timer do quiz
    if quiz_timer > 0:
        quiz_timer -= 1
        if quiz_timer == 0:
            quiz_mensagem = ""

    # 1. Eventos ───────────────────────────────────────────────────────────────
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

        if estado_jogo == "MENU":
            for botao in botoes_menu:
                botao.verificar_click(event)

        elif estado_jogo == "JOGANDO":
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_a, pygame.K_LEFT):
                    moving_left = True
                if event.key in (pygame.K_d, pygame.K_RIGHT):
                    moving_right = True
                if event.key in (pygame.K_w, pygame.K_UP, pygame.K_SPACE):
                    jump_pressed = True
                if event.key == pygame.K_ESCAPE:
                    estado_jogo = "PAUSADO"
            elif event.type == pygame.KEYUP:
                if event.key in (pygame.K_a, pygame.K_LEFT):
                    moving_left = False
                if event.key in (pygame.K_d, pygame.K_RIGHT):
                    moving_right = False

        elif estado_jogo == "QUIZ":
            resposta = None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    resposta = "A"
                elif event.key == pygame.K_2:
                    resposta = "B"
                elif event.key == pygame.K_3:
                    resposta = "C"
                elif event.key == pygame.K_4:
                    resposta = "D"
                elif event.key == pygame.K_5:
                    resposta = "E"
                elif event.key == pygame.K_ESCAPE:
                    # Sair do quiz sem responder (voltar ao jogo)
                    estado_jogo = "JOGANDO"

            if resposta and indice < len(perguntas):
                if resposta == perguntas[indice]["resposta"]:
                    pontuacao += 1
                    quiz_mensagem = "ACERTOU!!!"
                else:
                    quiz_mensagem = f"ERROU!!! A resposta correta era {perguntas[indice]['resposta']}"
                
                quiz_timer = 60  # Mostrar mensagem por 1 segundo (60 frames)
                indice += 1
                
                # Verificar se acabaram as perguntas
                if indice >= len(perguntas):
                    # Voltar para o jogo
                    estado_jogo = "JOGANDO"
                    # Remover o item coletado
                    if item_para_remover and item_para_remover in itens:
                        itens.remove(item_para_remover)
                    item_para_remover = None
                    # Dar recompensa ao jogador
                    if player:
                        player.player_health = min(player.player_health + 20, constants.PLAYER_HEALTH)

        elif estado_jogo == "PAUSADO":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                estado_jogo = "JOGANDO"
            for botao in botoes_pausa:
                botao.verificar_click(event)

        elif estado_jogo == "GAME_OVER":
            for botao in botoes_game_over:
                botao.verificar_click(event)

        elif estado_jogo == "CONFIGURACOES":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                estado_jogo = "MENU"
            menu_cfg.handle_event(event)

        elif estado_jogo == "CREDITOS":
            tela_creditos.handle_event(event)

    # 2. Atualização ───────────────────────────────────────────────────────────
    if estado_jogo == "JOGANDO" and player:
        dx = (moving_right - moving_left) * constants.PLAYER_SPEED
        if jump_pressed:
            if player.jump():
                jump_pressed = False

        player.move(dx, world.obstacles if world else [])
        atualizar_camera()

        player.update_invulnerable()

        for enemy in enemies:
            enemy.update(world.obstacles if world else [])
            enemy.check_player_collision(player)

        # Verificar coleta de itens
        for item in itens[:]:  # Usar cópia da lista
            if item.verificar_coleta(player):
                estado_jogo = "QUIZ"
                indice = 0
                item_para_remover = item
                break  # Sair do loop após encontrar um item

        if not player.alive or player.rect.top > constants.MAP_ROWS * constants.TILE_SIZE:
            estado_jogo = "GAME_OVER"

    # 3. Renderização ──────────────────────────────────────────────────────────
    if estado_jogo == "MENU":
        screen.blit(background_img, (0, 0))
        titulo = fonte_titulo.render("I . S . A", True, constants.YELLOW)
        screen.blit(titulo, titulo.get_rect(center=(constants.SCREEN_WIDTH // 2, 120)))
        for botao in botoes_menu:
            botao.desenhar(screen, mouse_pos)
    
    elif estado_jogo in ("JOGANDO", "PAUSADO"):
        dx = (moving_right - moving_left) * constants.PLAYER_SPEED
        desenhar_paralaxe(dx)

        if world:
            world.render(screen, camera_x, camera_y)
        if constants.DEBUG:
            draw_grid()

        for enemy in enemies:
            enemy.draw(screen, camera_x, camera_y)

        for item in itens:
            item.draw(screen, camera_x, camera_y)

        if player:
            player.draw(screen, camera_x, camera_y)
            
            # Desenhar barra de vida
            BAR_W, BAR_H = 200, 18
            BAR_X, BAR_Y = 10, 10
            proporcao = max(0, player.player_health / constants.PLAYER_HEALTH)
            pygame.draw.rect(screen, constants.RED, (BAR_X, BAR_Y, BAR_W, BAR_H), border_radius=4)
            pygame.draw.rect(screen, constants.GREEN, (BAR_X, BAR_Y, int(BAR_W * proporcao), BAR_H), border_radius=4)
            pygame.draw.rect(screen, constants.WHITE, (BAR_X, BAR_Y, BAR_W, BAR_H), 2, border_radius=4)
            
            # Desenhar pontuação
            score_surf = fonte_ui.render(f"Pontos: {pontuacao}", True, constants.WHITE)
            screen.blit(score_surf, (constants.SCREEN_WIDTH - 150, 10))

        hint = fonte_titulo.render("ESC = Pausa", True, constants.WHITE)
        screen.blit(hint, (10, 40))

        if estado_jogo == "PAUSADO":
            overlay = pygame.Surface(
                (constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT), pygame.SRCALPHA
            )
            overlay.fill((0, 0, 0, 160))
            screen.blit(overlay, (0, 0))

            surf = fonte_ui.render("PAUSADO", True, constants.YELLOW)
            rect = surf.get_rect(center=(constants.SCREEN_WIDTH // 2, 150))
            screen.blit(surf, rect)

            for botao in botoes_pausa:
                botao.desenhar(screen, mouse_pos)

    elif estado_jogo == "QUIZ":
        if indice < len(perguntas):
            desenhar_pergunta(perguntas[indice])
            
            # Desenhar mensagem de feedback
            if quiz_mensagem:
                surf = fonte_ui.render(quiz_mensagem, True, constants.YELLOW)
                screen.blit(surf, (50, 500))
            
            # Desenhar instruções
            instrucao = fonte_titulo.render("Pressione 1,2,3,4,5 para responder | ESC para sair", True, constants.WHITE)
            screen.blit(instrucao, (50, constants.SCREEN_HEIGHT - 50))
            
            # Desenhar pontuação
            score_surf = fonte_ui.render(f"Pontuação: {pontuacao}/{len(perguntas)}", True, constants.WHITE)
            screen.blit(score_surf, (constants.SCREEN_WIDTH - 250, 50))
            
            # Desenhar barra de progresso
            PROG_W = constants.SCREEN_WIDTH - 100
            PROG_H = 20
            PROG_X = 50
            PROG_Y = 30
            proporcao = indice / len(perguntas)
            pygame.draw.rect(screen, constants.GRAY, (PROG_X, PROG_Y, PROG_W, PROG_H), border_radius=10)
            pygame.draw.rect(screen, constants.GREEN, (PROG_X, PROG_Y, int(PROG_W * proporcao), PROG_H), border_radius=10)
            pygame.draw.rect(screen, constants.WHITE, (PROG_X, PROG_Y, PROG_W, PROG_H), 2, border_radius=10)
        else:
            # Caso algo dê errado, voltar ao jogo
            estado_jogo = "JOGANDO"

    elif estado_jogo == "GAME_OVER":
        screen.blit(background_img, (0, 0))
        overlay = pygame.Surface(
            (constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT), pygame.SRCALPHA
        )
        overlay.fill((0, 0, 0, 160))
        screen.blit(overlay, (0, 0))

        surf = fonte_ui.render("GAME OVER", True, constants.RED)
        rect = surf.get_rect(center=(constants.SCREEN_WIDTH // 2, 180))
        screen.blit(surf, rect)
        
        # Mostrar pontuação final
        score_surf = fonte_ui.render(f"Pontuação Final: {pontuacao}", True, constants.YELLOW)
        score_rect = score_surf.get_rect(center=(constants.SCREEN_WIDTH // 2, 240))
        screen.blit(score_surf, score_rect)

        for botao in botoes_game_over:
            botao.desenhar(screen, mouse_pos)

    elif estado_jogo == "CONFIGURACOES":
        screen.blit(background_img, (0, 0))
        menu_cfg.desenhar()

    elif estado_jogo == "CREDITOS":
        screen.blit(background_img, (0, 0))
        tela_creditos.update()
        tela_creditos.desenhar()

    # 4. Flip ──────────────────────────────────────────────────────────────────
    pygame.display.update()

pygame.quit()