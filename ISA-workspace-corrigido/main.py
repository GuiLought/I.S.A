import pygame
import sys
import constants
from src.character import Character
from src.buttons import Botao
from src.world import World
from pygame import mixer
from utils import carregar_imagem, carregar_tile, carregar_fonte, carregar_nivel_csv

# ── Inicialização ─────────────────────────────────────────────────────────────
mixer.init()
pygame.init()

screen = pygame.display.set_mode((constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT))
pygame.display.set_caption("I.S.A - Projeto QA")
clock = pygame.time.Clock()

# ── Estados possíveis ─────────────────────────────────────────────────────────
# "MENU" | "HISTORIA" | "SELECAO_AMBIENTE" | "JOGANDO" | "PAUSADO" | "GAME_OVER"
estado_jogo = "MENU"

# ── Tamanho da tela ───────────────────────────────────────────────────────────
TAM = (constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT)

# ── Ambientes ─────────────────────────────────────────────────────────────────
AMBIENTES = [
    {
        "nome":       "Pátio da Escola",
        "background": ("tela_menu", "FundoMenu.png"),
        "csv":        "level1_data.csv",
        "tile":       "tile_brick.png",
    },
    {
        "nome":       "Entrada CEFSA",
        "background": ("tela_menu", "FundoHistoria.png"),
        "csv":        "level2_data.csv",
        "tile":       "tile_brick.png",
    },
    {
        "nome":       "Arena / Quadra",
        "background": ("tela_menu", "Fundo_escola.jpg"),
        "csv":        "level3_data.csv",
        "tile":       "tile_brick.png",
    },
]
ambiente_atual = 0

# ── Recursos permanentes (carregados uma vez) ─────────────────────────────────
bg_menu     = carregar_imagem("tela_menu", "Fundo_escola.jpg",  TAM)
bg_historia = carregar_imagem("tela_menu", "FundoHistoria.png", TAM)
bg_selecao  = carregar_imagem("tela_menu", "FundoMenu.png",     TAM)

fonte_ui     = carregar_fonte("upheavtt.ttf", 28)
fonte_titulo = carregar_fonte("upheavtt.ttf", 18)

# ── Variáveis de jogo ─────────────────────────────────────────────────────────
player          = None
world           = None
background_jogo = None
camera_x = camera_y = 0
moving_left = moving_right = False
jump_pressed = False


# ── Funções auxiliares ────────────────────────────────────────────────────────
def draw_overlay(alpha=160):
    """Overlay escuro semitransparente sobre a tela inteira."""
    surf = pygame.Surface(TAM, pygame.SRCALPHA)
    surf.fill((0, 0, 0, alpha))
    screen.blit(surf, (0, 0))


def draw_overlay_texto(linhas, fonte=None):
    """Overlay com lista de (texto, cor) centralizado verticalmente."""
    if fonte is None:
        fonte = fonte_ui

    draw_overlay()

    total_h = len(linhas) * 50
    start_y = (constants.SCREEN_HEIGHT - total_h) // 2
    for i, (texto, cor) in enumerate(linhas):
        surf = fonte.render(texto, True, cor)
        rect = surf.get_rect(center=(constants.SCREEN_WIDTH // 2, start_y + i * 50))
        screen.blit(surf, rect)


# ── Carregamento do nível ─────────────────────────────────────────────────────
def carregar_recursos_jogo():
    global player, world, camera_x, camera_y
    global moving_left, moving_right, jump_pressed, background_jogo

    amb = AMBIENTES[ambiente_atual]
    background_jogo = carregar_imagem(amb["background"][0], amb["background"][1], TAM)

    tile_surface = carregar_tile(amb["tile"], constants.TILE_SIZE)
    tile_list    = [tile_surface] * constants.TILE_TYPES
    world_data   = carregar_nivel_csv(amb["csv"])

    world = World()
    world.process_data(world_data, tile_list)

    player_image = carregar_imagem("personagens", "link-teste.png")
    player = Character(
        constants.PLAYER_START_X,
        constants.PLAYER_START_Y,
        constants.PLAYER_SIZE,
        constants.PLAYER_SPEED,
        player_image,
    )

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
            (0,                      y * constants.TILE_SIZE - camera_y % constants.TILE_SIZE),
            (constants.SCREEN_WIDTH, y * constants.TILE_SIZE - camera_y % constants.TILE_SIZE),
        )


# ── Ações dos botões ──────────────────────────────────────────────────────────
def abrir_historia():
    global estado_jogo
    estado_jogo = "HISTORIA"

def abrir_selecao():
    global estado_jogo
    estado_jogo = "SELECAO_AMBIENTE"

def configurar_jogo():
    # TODO: implementar tela de configurações
    pass

def encerrar_jogo():
    pygame.quit()
    sys.exit()

def retomar_jogo():
    global estado_jogo
    estado_jogo = "JOGANDO"

def voltar_menu():
    global estado_jogo, player, world, background_jogo
    player = world = background_jogo = None
    estado_jogo = "MENU"

def voltar_selecao():
    global estado_jogo, player, world, background_jogo
    player = world = background_jogo = None
    estado_jogo = "SELECAO_AMBIENTE"

def selecionar_ambiente(indice):
    global ambiente_atual, estado_jogo
    ambiente_atual = indice
    carregar_recursos_jogo()
    estado_jogo = "JOGANDO"


# ── Botões ────────────────────────────────────────────────────────────────────
cx = (constants.SCREEN_WIDTH // 2) - (constants.BTN_LARGURA // 2)

botoes_menu = [
    Botao("JOGAR",         600,  10, constants.BTN_LARGURA, constants.BTN_ALTURA, abrir_historia),
    Botao("CONFIGURAÇÕES", 600,  80, constants.BTN_LARGURA, constants.BTN_ALTURA, configurar_jogo),
    Botao("SAIR",          600, 150, constants.BTN_LARGURA, constants.BTN_ALTURA, encerrar_jogo),
]

botoes_historia = [
    Botao("CONTINUAR", cx, 480, constants.BTN_LARGURA, constants.BTN_ALTURA, abrir_selecao),
    Botao("← VOLTAR",  cx, 550, constants.BTN_LARGURA, constants.BTN_ALTURA, voltar_menu),
]

botoes_selecao = []
for i, amb in enumerate(AMBIENTES):
    def _acao(idx=i):
        selecionar_ambiente(idx)
    botoes_selecao.append(
        Botao(amb["nome"], cx, 160 + i * 90, constants.BTN_LARGURA, constants.BTN_ALTURA, _acao)
    )
botoes_selecao.append(
    Botao("← VOLTAR", cx, 160 + len(AMBIENTES) * 90,
        constants.BTN_LARGURA, constants.BTN_ALTURA, voltar_menu)
)

botoes_pausa = [
    Botao("RETOMAR",     cx, 200, constants.BTN_LARGURA, constants.BTN_ALTURA, retomar_jogo),
    Botao("TROCAR FASE", cx, 290, constants.BTN_LARGURA, constants.BTN_ALTURA, voltar_selecao),
    Botao("MENU",        cx, 380, constants.BTN_LARGURA, constants.BTN_ALTURA, voltar_menu),
]

botoes_game_over = [
    Botao("REINICIAR", cx, 280, constants.BTN_LARGURA, constants.BTN_ALTURA, carregar_recursos_jogo),
    Botao("MENU",      cx, 370, constants.BTN_LARGURA, constants.BTN_ALTURA, voltar_menu),
]


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

        elif estado_jogo == "HISTORIA":
            for botao in botoes_historia:
                botao.verificar_click(event)
            if event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_SPACE):
                abrir_selecao()

        elif estado_jogo == "SELECAO_AMBIENTE":
            for botao in botoes_selecao:
                botao.verificar_click(event)

        elif estado_jogo == "JOGANDO":
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_a, pygame.K_LEFT):               moving_left  = True
                if event.key in (pygame.K_d, pygame.K_RIGHT):              moving_right = True
                if event.key in (pygame.K_w, pygame.K_UP, pygame.K_SPACE): jump_pressed = True
                if event.key == pygame.K_ESCAPE:                            estado_jogo  = "PAUSADO"
            elif event.type == pygame.KEYUP:
                if event.key in (pygame.K_a, pygame.K_LEFT):  moving_left  = False
                if event.key in (pygame.K_d, pygame.K_RIGHT): moving_right = False

        elif estado_jogo == "PAUSADO":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                estado_jogo = "JOGANDO"
            for botao in botoes_pausa:
                botao.verificar_click(event)

        elif estado_jogo == "GAME_OVER":
            for botao in botoes_game_over:
                botao.verificar_click(event)

    # 2. Atualização ───────────────────────────────────────────────────────────
    if estado_jogo == "JOGANDO" and player:
        dx = (moving_right - moving_left) * constants.PLAYER_SPEED

        # jump_pressed só é consumido se o pulo realmente aconteceu (player no chão)
        if jump_pressed:
            if player.jump():
                jump_pressed = False

        player.move(dx, world.obstacles if world else [])
        atualizar_camera()

        if player.rect.top > constants.MAP_ROWS * constants.TILE_SIZE:
            estado_jogo = "GAME_OVER"

    # 3. Renderização ──────────────────────────────────────────────────────────
    if estado_jogo == "MENU":
        screen.blit(bg_menu, (0, 0))
        titulo = fonte_titulo.render("I . S . A", True, constants.YELLOW)
        screen.blit(titulo, titulo.get_rect(center=(constants.SCREEN_WIDTH // 2, 120)))
        for botao in botoes_menu:
            botao.desenhar(screen, mouse_pos)

    elif estado_jogo == "HISTORIA":
        screen.blit(bg_historia, (0, 0))
        draw_overlay(100)
        linhas = [
            "A I.S.A foi criada para proteger o CEFSA...",
            "Mas algo ameaça o campus.",
            "Sua missão começa agora.",
        ]
        for i, linha in enumerate(linhas):
            surf = fonte_titulo.render(linha, True, constants.WHITE)
            screen.blit(surf, surf.get_rect(center=(constants.SCREEN_WIDTH // 2, 320 + i * 40)))
        dica = fonte_titulo.render("ESPAÇO / ENTER para continuar", True, constants.YELLOW)
        screen.blit(dica, dica.get_rect(center=(constants.SCREEN_WIDTH // 2, 450)))
        for botao in botoes_historia:
            botao.desenhar(screen, mouse_pos)

    elif estado_jogo == "SELECAO_AMBIENTE":
        screen.blit(bg_selecao, (0, 0))
        draw_overlay(120)
        titulo = fonte_ui.render("ESCOLHA O AMBIENTE", True, constants.YELLOW)
        screen.blit(titulo, titulo.get_rect(center=(constants.SCREEN_WIDTH // 2, 90)))
        for botao in botoes_selecao:
            botao.desenhar(screen, mouse_pos)

    elif estado_jogo in ("JOGANDO", "PAUSADO"):
        fundo = background_jogo if background_jogo else bg_menu
        screen.blit(fundo, (0, 0))
        if world:
            world.render(screen, camera_x, camera_y)
        if constants.DEBUG:
            draw_grid()
        if player:
            player.draw(screen, camera_x, camera_y)
        hint = fonte_titulo.render("ESC = Pausa", True, constants.WHITE)
        screen.blit(hint, (10, 10))
        nome_amb = fonte_titulo.render(AMBIENTES[ambiente_atual]["nome"], True, constants.YELLOW)
        screen.blit(nome_amb, nome_amb.get_rect(topright=(constants.SCREEN_WIDTH - 10, 10)))

        if estado_jogo == "PAUSADO":
            draw_overlay()
            surf = fonte_ui.render("PAUSADO", True, constants.YELLOW)
            screen.blit(surf, surf.get_rect(center=(constants.SCREEN_WIDTH // 2, 130)))
            for botao in botoes_pausa:
                botao.desenhar(screen, mouse_pos)

    elif estado_jogo == "GAME_OVER":
        fundo = background_jogo if background_jogo else bg_menu
        screen.blit(fundo, (0, 0))
        draw_overlay()
        surf = fonte_ui.render("GAME  OVER", True, constants.RED)
        screen.blit(surf, surf.get_rect(center=(constants.SCREEN_WIDTH // 2, 180)))
        for botao in botoes_game_over:
            botao.desenhar(screen, mouse_pos)

    # 4. Flip ──────────────────────────────────────────────────────────────────
    pygame.display.update()

pygame.quit()