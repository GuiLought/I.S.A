import pygame
import sys
import constants
from src.character import Character
from src.buttons import Botao, BotaoConfig, BotaoSair
from src.world import World
from src.enemies.enemy import Enemy
from src.configuracoes import MenuConfiguracoes
from src.creditos import TelaCreditos
from pygame import mixer
from utils import carregar_imagem, carregar_tile, carregar_fonte, carregar_nivel_csv

# ── Inicialização ─────────────────────────────────────────────────────────────
mixer.init()
pygame.init()

screen = pygame.display.set_mode((constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT))
pygame.display.set_caption("I.S.A - Projeto QA")
clock = pygame.time.Clock()

# ── Estados possíveis ─────────────────────────────────────────────────────────
# "MENU" | "JOGANDO" | "PAUSADO" | "GAME_OVER" | "CONFIGURACOES" | "CREDITOS"
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
camera_x = 0
camera_y = 0
moving_left = moving_right = False
jump_pressed = False


# ── Carregamento do nível ─────────────────────────────────────────────────────
def carregar_recursos_jogo():
    global player, world, enemies, camera_x, camera_y
    global moving_left, moving_right, jump_pressed

    tile_surface = carregar_tile("tile_brick.png", constants.TILE_SIZE)
    tile_list    = [tile_surface] * constants.TILE_TYPES

    world_data = carregar_nivel_csv("level1_data.csv")

    world = World()
    world.process_data(world_data, tile_list)

    player_image = carregar_imagem("personagens", "areninha_ISA.png")
    player = Character(
        constants.PLAYER_START_X,
        constants.PLAYER_START_Y,
        constants.PLAYER_SIZE,
        constants.PLAYER_SPEED,
        player_image,
        constants.PLAYER_HEALTH,
    )

    # Inimigo posicionado no mesmo chão que o player, mais à direita
    enemies = [
        Enemy(
            x=constants.PLAYER_START_X + 300,
            y=constants.PLAYER_START_Y,
        )
    ]

    camera_x = camera_y = 0
    moving_left = moving_right = jump_pressed = False


# ── Câmera ────────────────────────────────────────────────────────────────────
def atualizar_camera():
    global camera_x, camera_y

    target_x = player.rect.centerx - constants.SCREEN_WIDTH  // 2
    target_y = player.rect.centery - constants.SCREEN_HEIGHT // 2

    map_w = constants.MAP_COLS * constants.TILE_SIZE
    map_h = constants.MAP_ROWS * constants.TILE_SIZE

    camera_x = max(0, min(target_x, map_w - constants.SCREEN_WIDTH))
    camera_y = max(0, min(target_y, map_h - constants.SCREEN_HEIGHT))


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

# ── Menu de Configurações e Créditos (do I.S.A-main) ─────────────────────────
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

        # Atualiza inimigos
        for enemy in enemies:
            enemy.update(world.obstacles if world else [])
            enemy.check_player_collision(player)

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

        if player:
            player.draw(screen, camera_x, camera_y)

        hint = fonte_titulo.render("ESC = Pausa", True, constants.WHITE)
        screen.blit(hint, (10, 10))

        # ── Barra de vida ─────────────────────────────────────────────────────
        if player:
            BAR_W, BAR_H = 200, 18
            BAR_X, BAR_Y = 10, 35
            proporcao = max(0, player.player_health / constants.PLAYER_HEALTH)
            pygame.draw.rect(screen, constants.RED,   (BAR_X, BAR_Y, BAR_W, BAR_H), border_radius=4)
            pygame.draw.rect(screen, constants.GREEN, (BAR_X, BAR_Y, int(BAR_W * proporcao), BAR_H), border_radius=4)
            pygame.draw.rect(screen, constants.WHITE, (BAR_X, BAR_Y, BAR_W, BAR_H), 2, border_radius=4)

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

    elif estado_jogo == "GAME_OVER":
        screen.blit(background_img, (0, 0))
        overlay = pygame.Surface(
            (constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT), pygame.SRCALPHA
        )
        overlay.fill((0, 0, 0, 160))
        screen.blit(overlay, (0, 0))

        surf = fonte_ui.render("GAME  OVER", True, constants.RED)
        rect = surf.get_rect(center=(constants.SCREEN_WIDTH // 2, 180))
        screen.blit(surf, rect)

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
