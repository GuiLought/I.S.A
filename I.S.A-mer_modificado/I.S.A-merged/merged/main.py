import pygame
import sys
import random
import constants
from src.character import Character
from src.buttons import Botao, BotaoConfig, BotaoSair
from src.world import World
from src.enemies.enemy import Enemy
from src.configuracoes import MenuConfiguracoes
from src.creditos import TelaCreditos
from src.itens.minerio_cobre import minerio_cobre
from pygame import mixer
from utils import carregar_imagem, carregar_tile, carregar_fonte, carregar_nivel_csv, carregar_perguntas_csv

# ── Inicialização ─────────────────────────────────────────────────────────────
BASE_W = 800
BASE_H = 600

screen = None
clock = None

constants.SCREEN_WIDTH  = BASE_W
constants.SCREEN_HEIGHT = BASE_H

# ── Estados possíveis ─────────────────────────────────────────────────────────
# "INTRO" | "MENU" | "HISTORIA" | "JOGANDO" | "PAUSADO" | "GAME_OVER" | "QUIZ" | "CONFIGURACOES" | "CREDITOS"
estado_jogo = "INTRO"

# ── Escala proporcional ───────────────────────────────────────────────────────
def sx(v): return int(v * constants.SCREEN_WIDTH  / BASE_W)
def sy(v): return int(v * constants.SCREEN_HEIGHT / BASE_H)
def sf(v): return max(8, int(v * min(constants.SCREEN_WIDTH / BASE_W,
                                        constants.SCREEN_HEIGHT / BASE_H)))

# ── Recursos reescaláveis ─────────────────────────────────────────────────────
background_img = None
paralaxe_c1    = None
paralaxe_c2    = None
fonte_ui       = None
fonte_titulo   = None
botoes_menu    = []
botoes_pausa   = []
botoes_game_over = []
menu_cfg       = None
tela_creditos  = None

VEL_C1    = 4
VEL_C2    = 1
offset_c1 = 0
offset_c2 = 0

def recriar_ui():
    global background_img, paralaxe_c1, paralaxe_c2
    global fonte_ui, fonte_titulo
    global botoes_menu, botoes_pausa, botoes_game_over
    global menu_cfg, tela_creditos

    W = constants.SCREEN_WIDTH
    H = constants.SCREEN_HEIGHT

    background_img = carregar_imagem("tela_menu", "Tela_Menu_Principal.jpg", (W, H))

    img_c1 = carregar_imagem("backgrounds", "C1.png")
    img_c2 = carregar_imagem("backgrounds", "C2.png")
    paralaxe_c1 = pygame.transform.scale(img_c1, (img_c1.get_width() * H // img_c1.get_height(), H))
    paralaxe_c2 = pygame.transform.scale(img_c2, (img_c2.get_width() * H // img_c2.get_height(), H))

    fonte_ui     = carregar_fonte("upheavtt.ttf", sf(28))
    fonte_titulo = carregar_fonte("upheavtt.ttf", sf(18))

    btn_w = max(180, sx(200))  # Largura mínima dos botões
    btn_h = max(50, sy(60))    # Altura mínima dos botões
    x_c   = W // 2 - btn_w // 2

    botoes_menu = [
        Botao("JOGAR", sx(300), sy(500), btn_w, btn_h, iniciar_jogo),
        BotaoSair(cx=sx(700), cy=sy(38), raio=max(25, sx(30)), acao=encerrar_jogo),
        BotaoConfig(cx=sx(762), cy=sy(38), raio=max(25, sx(30)), acao=configurar_jogo),
    ]
    botoes_pausa = [
        Botao("RETOMAR", x_c, sy(220), btn_w, btn_h, retomar_jogo),
        Botao("MENU",    x_c, sy(310), btn_w, btn_h, voltar_menu),
    ]
    botoes_game_over = [
        Botao("REINICIAR", x_c, sy(280), btn_w, btn_h, iniciar_jogo),
        Botao("MENU",      x_c, sy(360), btn_w, btn_h, voltar_menu),
    ]

    menu_cfg = MenuConfiguracoes(screen, W, H,
        callback_voltar=voltar_menu, callback_creditos=abrir_creditos)
    tela_creditos = TelaCreditos(screen, W, H, callback_voltar=voltar_menu)

# ── Paralaxe ──────────────────────────────────────────────────────────────────
def desenhar_paralaxe(camera_x=0):
    screen.fill((0, 0, 0))
    larg_c2 = paralaxe_c2.get_width()
    off_c2  = int(-camera_x * 0.25) % larg_c2
    for x in range(-larg_c2, constants.SCREEN_WIDTH + larg_c2, larg_c2):
        screen.blit(paralaxe_c2, (x + off_c2, 0))
    larg_c1 = paralaxe_c1.get_width()
    off_c1  = int(-camera_x * 0.50) % larg_c1
    for x in range(-larg_c1, constants.SCREEN_WIDTH + larg_c1, larg_c1):
        screen.blit(paralaxe_c1, (x + off_c1, 0))



# ── Intro do personagem ─────────────────────────────────────────────────────
intro_personagem_img = None
intro_personagem_rect = None
intro_personagem_x = -200
intro_personagem_y = 0
intro_velocidade = 5
intro_animacao_finalizada = False
intro_frames = []
intro_frame_index = 0
intro_frame_counter = 0
intro_frame_delay = 8
texto_historia = [
    "Placeholder de texto da historia.",
    "Aqui entrara o conteudo final depois.",
    "Clique em qualquer lugar para voltar ao menu."
]

def inicializar_intro():
    global intro_personagem_img, intro_personagem_rect
    global intro_personagem_x, intro_personagem_y, intro_animacao_finalizada
    global intro_frames, intro_frame_index, intro_frame_counter

    frame_names = ["S1.png", "S2.png", "S3.png", "S4.png", "S5.png", "S7.png"]
    intro_frames = []
    for nome in frame_names:
        try:
            sprite = carregar_imagem("personagens", nome)
            intro_frames.append(pygame.transform.scale(sprite, (140, 140)))
        except Exception:
            continue

    if not intro_frames:
        try:
            fallback = carregar_imagem("personagens", "Areninha4 2.png")
            intro_frames = [pygame.transform.scale(fallback, (140, 140))]
        except Exception:
            intro_frames = []

    intro_frame_index = 0
    intro_frame_counter = 0
    intro_personagem_img = intro_frames[0] if intro_frames else None
    intro_personagem_x = -140
    intro_personagem_y = constants.SCREEN_HEIGHT - 170
    intro_personagem_rect = intro_personagem_img.get_rect(topleft=(intro_personagem_x, intro_personagem_y)) if intro_personagem_img else None
    intro_animacao_finalizada = False

def abrir_historia():
    global estado_jogo
    estado_jogo = "HISTORIA"

# ── Variáveis de jogo ─────────────────────────────────────────────────────────
player   = None
world    = None
enemies  = []
itens    = []
camera_x = 0
camera_y = 0
moving_left = moving_right = False
jump_pressed = False

perguntas         = []
pontuacao         = 0
indice            = 0
quiz_mensagem     = ""
quiz_timer        = 0
item_para_remover = None


def reiniciar_movimento():
    global moving_left, moving_right, jump_pressed
    moving_left = moving_right = jump_pressed = False



def carregar_perguntas():
    try:
        return carregar_perguntas_csv("perguntas.csv")
    except Exception as e:
        print(f"AVISO: Erro ao carregar perguntas: {e}")
        return []

perguntas = carregar_perguntas()

# ── Carregamento do nível ─────────────────────────────────────────────────────
def carregar_recursos_jogo():
    global player, world, enemies, itens, camera_x, camera_y
    global moving_left, moving_right, jump_pressed
    global pontuacao, indice, quiz_mensagem, quiz_timer, item_para_remover

    tile_surface = carregar_tile("tile_brick.png", constants.TILE_SIZE)
    tile_list    = [tile_surface] * constants.TILE_TYPES
    world_data   = carregar_nivel_csv("level1_data.csv")

    world = World()
    world.process_data(world_data, tile_list)

    player_image = carregar_imagem("personagens", "areninha_ISA.png")
    player = Character(
        constants.PLAYER_START_X, constants.PLAYER_START_Y,
        constants.PLAYER_SIZE, constants.PLAYER_SPEED,
        player_image, constants.PLAYER_HEALTH,
    )

    enemies = [Enemy(x=constants.PLAYER_START_X + 300, y=constants.PLAYER_START_Y)]

    itens = [
        minerio_cobre("m_minerio.png", x=600, y=constants.PLAYER_START_Y, tamanho=(40, 40)),
        minerio_cobre("m_minerio.png", x=900, y=constants.PLAYER_START_Y, tamanho=(40, 40)),
    ]

    camera_x = camera_y = 0
    reiniciar_movimento()
    pontuacao = 0; indice = 0; quiz_mensagem = ""; quiz_timer = 0; item_para_remover = None

# ── Câmera ────────────────────────────────────────────────────────────────────
def atualizar_camera():
    global camera_x, camera_y
    target_x = player.rect.centerx - constants.SCREEN_WIDTH  // 2
    target_y = player.rect.centery - constants.SCREEN_HEIGHT // 2
    map_w = constants.MAP_COLS * constants.TILE_SIZE
    map_h = constants.MAP_ROWS * constants.TILE_SIZE
    camera_x = max(0, min(target_x, map_w - constants.SCREEN_WIDTH))
    camera_y = max(0, min(target_y, map_h - constants.SCREEN_HEIGHT))

# ── Tela de perguntas ─────────────────────────────────────────────────────────
def desenhar_pergunta(pergunta):
    screen.fill((0, 0, 0))
    header = fonte_titulo.render(
        f"{pergunta['disciplina']}  |  Nivel: {pergunta['nivel']}", True, constants.YELLOW)
    screen.blit(header, (sx(50), sy(60)))
    textos = [
        pergunta["pergunta"],
        "A) " + pergunta["opcao_a"],
        "B) " + pergunta["opcao_b"],
        "C) " + pergunta["opcao_c"],
        "D) " + pergunta["opcao_d"],
        "E) " + pergunta["opcao_e"],
    ]
    y = sy(110)
    for texto in textos:
        screen.blit(fonte_ui.render(texto, True, constants.WHITE), (sx(50), y))
        y += sy(50)

# ── Debug grid ────────────────────────────────────────────────────────────────
def draw_grid():
    for x in range(constants.SCREEN_WIDTH // constants.TILE_SIZE + 1):
        pygame.draw.line(screen, constants.WHITE,
            (x * constants.TILE_SIZE - camera_x % constants.TILE_SIZE, 0),
            (x * constants.TILE_SIZE - camera_x % constants.TILE_SIZE, constants.SCREEN_HEIGHT))
    for y in range(constants.SCREEN_HEIGHT // constants.TILE_SIZE + 1):
        pygame.draw.line(screen, constants.WHITE,
            (0, y * constants.TILE_SIZE - camera_y % constants.TILE_SIZE),
            (constants.SCREEN_WIDTH, y * constants.TILE_SIZE - camera_y % constants.TILE_SIZE))

# ── Ações dos botões ──────────────────────────────────────────────────────────
def iniciar_jogo():
    global estado_jogo
    random.shuffle(perguntas)
    carregar_recursos_jogo()
    estado_jogo = "JOGANDO"

def encerrar_jogo():
    pygame.quit(); sys.exit()

def configurar_jogo():
    global estado_jogo
    estado_jogo = "CONFIGURACOES"

def retomar_jogo():
    global estado_jogo
    estado_jogo = "JOGANDO"

def voltar_menu():
    global estado_jogo, player, world, enemies, itens
    player = world = None
    enemies = []; itens = []
    estado_jogo = "MENU"

def abrir_creditos():
    global estado_jogo
    estado_jogo = "CREDITOS"

# ── Criação da UI e loop principal ───────────────────────────────────────
if __name__ == "__main__":
    pygame.init()
    try:
        mixer.init()
    except pygame.error as e:
        print(f"AVISO: Mixer não pôde ser inicializado: {e}")

    screen = pygame.display.set_mode((BASE_W, BASE_H))
    pygame.display.set_caption("I.S.A")
    clock = pygame.time.Clock()

    constants.SCREEN_WIDTH  = screen.get_width()
    constants.SCREEN_HEIGHT = screen.get_height()
    recriar_ui()
    inicializar_intro()

    # ── Loop principal ────────────────────────────────────────────────────────────
    run = True
    while run:
        clock.tick(constants.FPS)
        mouse_pos = pygame.mouse.get_pos()

        if quiz_timer > 0:
            quiz_timer -= 1
            if quiz_timer == 0:
                quiz_mensagem = ""

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            # Toggle fullscreen com F11
            if event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
                if screen.get_flags() & pygame.FULLSCREEN:
                    screen = pygame.display.set_mode((BASE_W, BASE_H))
                else:
                    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                constants.SCREEN_WIDTH  = screen.get_width()
                constants.SCREEN_HEIGHT = screen.get_height()
                recriar_ui()  # recria botões e imagens na nova resolução

            if estado_jogo == "INTRO":
                if event.type in (pygame.MOUSEBUTTONDOWN, pygame.KEYDOWN) and intro_animacao_finalizada:
                    abrir_historia()

            elif estado_jogo == "MENU":
                for botao in botoes_menu:
                    botao.verificar_click(event)

            elif estado_jogo == "JOGANDO":
                if event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_a, pygame.K_LEFT):  moving_left  = True
                    if event.key in (pygame.K_d, pygame.K_RIGHT): moving_right = True
                    if event.key in (pygame.K_w, pygame.K_UP, pygame.K_SPACE): jump_pressed = True
                    if event.key == pygame.K_ESCAPE: estado_jogo = "PAUSADO"
                elif event.type == pygame.KEYUP:
                    if event.key in (pygame.K_a, pygame.K_LEFT):  moving_left  = False
                    if event.key in (pygame.K_d, pygame.K_RIGHT): moving_right = False

            elif estado_jogo == "QUIZ":
                resposta = None
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1: resposta = "a"
                    elif event.key == pygame.K_2: resposta = "b"
                    elif event.key == pygame.K_3: resposta = "c"
                    elif event.key == pygame.K_4: resposta = "d"
                    elif event.key == pygame.K_5: resposta = "e"
                    elif event.key == pygame.K_ESCAPE:
                        estado_jogo = "JOGANDO"
                        reiniciar_movimento()
                if resposta and indice < len(perguntas):
                    gabarito = perguntas[indice]["resposta"].strip().lower()
                    if resposta == gabarito:
                        pontuacao += 1
                        quiz_mensagem = "ACERTOU!!!"
                        if player and player.alive:
                            player.player_health = min(player.player_health + 20, constants.PLAYER_HEALTH)
                    else:
                        quiz_mensagem = f"ERROU!!! Resposta correta: {gabarito.upper()}"
                    quiz_timer = 60
                    indice += 1
                    reiniciar_movimento()

                    # Volta ao jogo após UMA pergunta
                    if item_para_remover and item_para_remover in itens:
                        itens.remove(item_para_remover)
                    item_para_remover = None
                    estado_jogo = "JOGANDO"

            elif estado_jogo == "PAUSADO":
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    estado_jogo = "JOGANDO"
                for botao in botoes_pausa:
                    botao.verificar_click(event)

            elif estado_jogo == "GAME_OVER":
                for botao in botoes_game_over:
                    botao.verificar_click(event)

            elif estado_jogo == "HISTORIA":
                if event.type in (pygame.MOUSEBUTTONDOWN, pygame.KEYDOWN):
                    voltar_menu()


            elif estado_jogo == "CONFIGURACOES":
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    estado_jogo = "MENU"
                menu_cfg.handle_event(event)

            elif estado_jogo == "CREDITOS":
                tela_creditos.handle_event(event)

        # 2. Atualização ───────────────────────────────────────────────────────────
        if estado_jogo == "INTRO":
            destino_x = sx(40)
            if intro_personagem_x < destino_x:
                intro_personagem_x += intro_velocidade
                if intro_personagem_rect:
                    intro_personagem_rect.x = intro_personagem_x
                intro_frame_counter += 1
                if intro_frame_counter >= intro_frame_delay:
                    intro_frame_counter = 0
                    intro_frame_index = (intro_frame_index + 1) % len(intro_frames) if intro_frames else 0
                    if intro_frames:
                        intro_personagem_img = intro_frames[intro_frame_index]
            else:
                intro_animacao_finalizada = True

        elif estado_jogo == "JOGANDO" and player:
            if jump_pressed:
                if player.jump(): jump_pressed = False
            dx = (moving_right - moving_left) * constants.PLAYER_SPEED
            player.move(dx, world.obstacles if world else [])
            atualizar_camera()
            player.update_invulnerable()
            for enemy in enemies:
                enemy.update(world.obstacles if world else [])
                enemy.check_player_collision(player)
            for item in itens[:]:
                if item.verificar_coleta(player):
                    estado_jogo = "QUIZ"
                    reiniciar_movimento()
                    item_para_remover = item
                    break
            if not player.alive or player.rect.top > constants.MAP_ROWS * constants.TILE_SIZE:
                estado_jogo = "GAME_OVER"

        # 3. Renderização ──────────────────────────────────────────────────────────
        W = constants.SCREEN_WIDTH
        H = constants.SCREEN_HEIGHT

        if estado_jogo == "INTRO":
            screen.fill((0, 0, 0))

            if intro_personagem_img:
                screen.blit(intro_personagem_img, intro_personagem_rect)

            if intro_animacao_finalizada:
                overlay = pygame.Surface((W, H), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 90))
                screen.blit(background_img, (0, 0))
                screen.blit(overlay, (0, 0))

                titulo = fonte_titulo.render("I . S . A", True, constants.YELLOW)
                screen.blit(titulo, titulo.get_rect(center=(W // 2, sy(120))))

                for botao in botoes_menu:
                    botao.desenhar(screen, mouse_pos)

                pygame.draw.rect(screen, constants.YELLOW, intro_personagem_rect.inflate(10, 10), 2, border_radius=10)
                dica = fonte_titulo.render("Clique no personagem", True, constants.WHITE)
                screen.blit(dica, (sx(20), intro_personagem_y - sy(40)))

                screen.blit(intro_personagem_img, intro_personagem_rect)

        elif estado_jogo == "MENU":
            screen.blit(background_img, (0, 0))
            titulo = fonte_titulo.render("I . S . A", True, constants.YELLOW)
            screen.blit(titulo, titulo.get_rect(center=(W // 2, sy(120))))
            for botao in botoes_menu:
                botao.desenhar(screen, mouse_pos)

        elif estado_jogo in ("JOGANDO", "PAUSADO"):
            desenhar_paralaxe(camera_x)
            if world:   world.render(screen, camera_x, camera_y)
            if constants.DEBUG: draw_grid()
            for enemy in enemies:
                if enemy:
                    enemy.draw(screen, camera_x, camera_y)
            for item in itens:
                if item:
                    item.draw(screen, camera_x, camera_y)
            if player and player.alive:
                player.draw(screen, camera_x, camera_y)

            hint = fonte_titulo.render("ESC = Pausa", True, constants.WHITE)
            screen.blit(hint, (sx(10), sy(10)))

            if player and player.alive:
                BAR_W = sx(200); BAR_H = sy(18)
                BAR_X = sx(10);  BAR_Y = sy(35)
                proporcao = max(0, min(1, player.player_health / constants.PLAYER_HEALTH))
                pygame.draw.rect(screen, constants.RED,   (BAR_X, BAR_Y, BAR_W, BAR_H), border_radius=4)
                pygame.draw.rect(screen, constants.GREEN, (BAR_X, BAR_Y, int(BAR_W * proporcao), BAR_H), border_radius=4)
                pygame.draw.rect(screen, constants.WHITE, (BAR_X, BAR_Y, BAR_W, BAR_H), 2, border_radius=4)
                score_surf = fonte_ui.render(f"Pontos: {pontuacao}", True, constants.WHITE)
                screen.blit(score_surf, (W - sx(160), sy(10)))

            if estado_jogo == "PAUSADO":
                overlay = pygame.Surface((W, H), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 160))
                screen.blit(overlay, (0, 0))
                surf = fonte_ui.render("PAUSADO", True, constants.YELLOW)
                screen.blit(surf, surf.get_rect(center=(W // 2, sy(150))))
                for botao in botoes_pausa:
                    botao.desenhar(screen, mouse_pos)

        elif estado_jogo == "QUIZ":
            if indice < len(perguntas):
                desenhar_pergunta(perguntas[indice])
                PROG_W = W - sx(100); PROG_H = sy(20); PROG_X = sx(50); PROG_Y = sy(30)
                proporcao = indice / len(perguntas)
                pygame.draw.rect(screen, constants.GRAY,  (PROG_X, PROG_Y, PROG_W, PROG_H), border_radius=10)
                pygame.draw.rect(screen, constants.GREEN, (PROG_X, PROG_Y, int(PROG_W * proporcao), PROG_H), border_radius=10)
                pygame.draw.rect(screen, constants.WHITE, (PROG_X, PROG_Y, PROG_W, PROG_H), 2, border_radius=10)
                score_surf = fonte_ui.render(f"Pontuacao: {pontuacao}/{len(perguntas)}", True, constants.WHITE)
                screen.blit(score_surf, (W - sx(250), sy(50)))
                if quiz_mensagem:
                    cor_msg = constants.GREEN if "ACERTOU" in quiz_mensagem else constants.RED
                    screen.blit(fonte_ui.render(quiz_mensagem, True, cor_msg), (sx(50), sy(500)))
                instrucao = fonte_titulo.render("Pressione 1-5 para responder  |  ESC para sair", True, constants.WHITE)
                screen.blit(instrucao, (sx(50), H - sy(50)))
            else:
                estado_jogo = "JOGANDO"

        elif estado_jogo == "GAME_OVER":
            screen.blit(background_img, (0, 0))
            overlay = pygame.Surface((W, H), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            screen.blit(overlay, (0, 0))
            surf = fonte_ui.render("GAME OVER", True, constants.RED)
            screen.blit(surf, surf.get_rect(center=(W // 2, sy(180))))
            score_surf = fonte_ui.render(f"Pontuacao Final: {pontuacao}", True, constants.YELLOW)
            screen.blit(score_surf, score_surf.get_rect(center=(W // 2, sy(240))))
            for botao in botoes_game_over:
                botao.desenhar(screen, mouse_pos)

        elif estado_jogo == "HISTORIA":
            screen.fill((15, 15, 15))
            titulo_historia = fonte_ui.render("TELA DE HISTORIA", True, constants.YELLOW)
            screen.blit(titulo_historia, titulo_historia.get_rect(center=(W // 2, sy(120))))

            y_texto = sy(220)
            for linha in texto_historia:
                texto_surface = fonte_titulo.render(linha, True, constants.WHITE)
                screen.blit(texto_surface, texto_surface.get_rect(center=(W // 2, y_texto)))
                y_texto += sy(50)

        elif estado_jogo == "HISTORIA":
            screen.fill((15, 15, 15))
            titulo_historia = fonte_ui.render("TELA DE HISTORIA", True, constants.YELLOW)
            screen.blit(titulo_historia, titulo_historia.get_rect(center=(W // 2, sy(120))))

            y_texto = sy(220)
            for linha in texto_historia:
                texto_surface = fonte_titulo.render(linha, True, constants.WHITE)
                screen.blit(texto_surface, texto_surface.get_rect(center=(W // 2, y_texto)))
                y_texto += sy(50)

        elif estado_jogo == "CONFIGURACOES":
            screen.blit(background_img, (0, 0))
            menu_cfg.desenhar()

        elif estado_jogo == "CREDITOS":
            screen.blit(background_img, (0, 0))
            tela_creditos.update()
            tela_creditos.desenhar()

        pygame.display.update()

    pygame.quit()