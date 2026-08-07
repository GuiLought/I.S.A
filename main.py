import random
import sys

import pygame
from pygame import mixer

import constants
from src.buttons import Botao, BotaoConfig, BotaoSair
from src.character import Character
from src.creditos import TelaCreditos
from src.enemies.enemy import Enemy
from src.itens.minerio_cobre import minerio_cobre
from src.telas import TelaConfiguracoes, TelaLogin
from src.world import World
from utils import (
    carregar_fonte,
    carregar_imagem,
    carregar_nivel_csv,
    carregar_perguntas_csv,
    carregar_tile,
)

# ── Inicialização ─────────────────────────────────────────────────────────────
BASE_W = 800
BASE_H = 600

screen = None
clock = None

constants.SCREEN_WIDTH = BASE_W
constants.SCREEN_HEIGHT = BASE_H

# ── Estados possíveis ─────────────────────────────────────────────────────────
estado_jogo = "MENU"


# ── Escala proporcional ───────────────────────────────────────────────────────
def sx(v):
    return int(v * constants.SCREEN_WIDTH / BASE_W)


def sy(v):
    return int(v * constants.SCREEN_HEIGHT / BASE_H)


def sf(v):
    return max(
        8,
        int(v * min(constants.SCREEN_WIDTH / BASE_W, constants.SCREEN_HEIGHT / BASE_H)),
    )


# ── TELA DE CARREGAMENTO ──────────────────────────────────────────────────────
def tela_carregamento(screen, progresso=0, mensagem="Carregando..."):
    W = constants.SCREEN_WIDTH
    H = constants.SCREEN_HEIGHT
    screen.fill((20, 20, 40))
    try:
        fonte_titulo = carregar_fonte("upheavtt.ttf", sf(48))
        titulo = fonte_titulo.render("I.S.A", True, (241, 187, 52))
        screen.blit(titulo, titulo.get_rect(center=(W // 2, H // 2 - 80)))
        fonte_msg = carregar_fonte("upheavtt.ttf", sf(20))
        texto = fonte_msg.render(mensagem, True, (200, 200, 200))
        screen.blit(texto, texto.get_rect(center=(W // 2, H // 2 - 20)))
    except:
        pass
    barra_w = 400
    barra_h = 20
    barra_x = (W - barra_w) // 2
    barra_y = H // 2 + 20
    pygame.draw.rect(
        screen, (60, 60, 80), (barra_x, barra_y, barra_w, barra_h), border_radius=10
    )
    pygame.draw.rect(
        screen,
        (76, 175, 80),
        (barra_x, barra_y, int(barra_w * progresso), barra_h),
        border_radius=10,
    )
    pygame.draw.rect(
        screen,
        (241, 187, 52),
        (barra_x, barra_y, barra_w, barra_h),
        2,
        border_radius=10,
    )
    pygame.display.flip()


# ── Recursos reescaláveis ─────────────────────────────────────────────────────
background_img = None
paralaxe_c1 = None
paralaxe_c2 = None
fonte_ui = None
fonte_titulo = None
botoes_menu = []
botoes_pausa = []
botoes_game_over = []
botao_voltar = None
tela_creditos = None
tela_login = None
tela_configuracoes = None


def recriar_ui():
    global background_img, paralaxe_c1, paralaxe_c2, fonte_ui, fonte_titulo
    global \
        botoes_menu, \
        botoes_pausa, \
        botoes_game_over, \
        tela_login, \
        tela_creditos, \
        tela_configuracoes, \
        botao_voltar
    tela_carregamento(screen, 0.1, "Carregando interface...")
    W, H = constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT
    background_img = carregar_imagem("tela_menu", "Tela_Menu_Principal.jpg", (W, H))
    tela_carregamento(screen, 0.3, "Carregando imagens...")
    img_c1 = carregar_imagem("backgrounds", "C1.png")
    img_c2 = carregar_imagem("backgrounds", "C2.png")
    paralaxe_c1 = pygame.transform.scale(
        img_c1, (img_c1.get_width() * H // img_c1.get_height(), H)
    )
    paralaxe_c2 = pygame.transform.scale(
        img_c2, (img_c2.get_width() * H // img_c2.get_height(), H)
    )
    tela_carregamento(screen, 0.5, "Carregando fontes...")
    fonte_ui = carregar_fonte("upheavtt.ttf", sf(28))
    fonte_titulo = carregar_fonte("upheavtt.ttf", sf(18))
    btn_w = max(180, sx(200))
    btn_h = max(50, sy(60))
    x_c = W // 2 - btn_w // 2
    tela_carregamento(screen, 0.7, "Carregando botões...")
    botoes_menu = [
        Botao("JOGAR", sx(300), sy(500), btn_w, btn_h, iniciar_jogo),
        BotaoSair(cx=sx(700), cy=sy(38), raio=max(25, sx(30)), acao=encerrar_jogo),
        BotaoConfig(cx=sx(762), cy=sy(38), raio=max(25, sx(30)), acao=configurar_jogo),
        Botao("LOGIN", sx(300), sy(400), btn_w, btn_h, abrir_login),
    ]
    botoes_pausa = [
        Botao("RETOMAR", x_c, sy(220), btn_w, btn_h, retomar_jogo),
        Botao("MENU", x_c, sy(310), btn_w, btn_h, voltar_menu),
    ]
    botoes_game_over = [
        Botao("REINICIAR", x_c, sy(280), btn_w, btn_h, iniciar_jogo),
        Botao("MENU", x_c, sy(360), btn_w, btn_h, voltar_menu),
    ]

    tela_creditos = TelaCreditos(screen, W, H, callback_voltar=voltar_menu)
    tela_carregamento(screen, 1.0, "Pronto!")
    pygame.time.wait(500)


# ── Paralaxe ──────────────────────────────────────────────────────────────────
def desenhar_paralaxe(camera_x=0):
    screen.fill((0, 0, 0))
    larg_c2 = paralaxe_c2.get_width()
    off_c2 = int(-camera_x * 0.25) % larg_c2
    for x in range(-larg_c2, constants.SCREEN_WIDTH + larg_c2, larg_c2):
        screen.blit(paralaxe_c2, (x + off_c2, 0))
    larg_c1 = paralaxe_c1.get_width()
    off_c1 = int(-camera_x * 0.50) % larg_c1
    for x in range(-larg_c1, constants.SCREEN_WIDTH + larg_c1, larg_c1):
        screen.blit(paralaxe_c1, (x + off_c1, 0))


# ── TELA DE PERGUNTA COM LAYOUT MELHORADO (SCROLL + CLIQUE NAS ALTERNATIVAS) ──
def desenhar_pergunta_melhorado(
    screen, pergunta, pontuacao, indice, total, mensagem="", tempo_msg=0
):
    global quiz_scroll, quiz_max_scroll, quiz_alt_rects, quiz_conteudo_rect

    W = constants.SCREEN_WIDTH
    H = constants.SCREEN_HEIGHT

    # Cores
    CORES = {
        "bg": (20, 20, 40),
        "box": (45, 45, 65),
        "box_alt": (55, 55, 75),
        "texto": (255, 255, 255),
        "titulo": (241, 187, 52),
        "destaque": (100, 200, 255),
        "verde": (76, 175, 80),
        "vermelho": (244, 67, 54),
        "cinza": (100, 100, 120),
    }

    # Fundo com gradiente suave
    for i in range(H):
        cor = (20 + i // 30, 20 + i // 30, 40 + i // 20)
        pygame.draw.line(screen, cor, (0, i), (W, i))

    # Caixa principal
    box_w = int(W * 0.82)
    box_h = int(H * 0.82)
    box_x = (W - box_w) // 2
    box_y = (H - box_h) // 2
    pygame.draw.rect(
        screen, CORES["box"], (box_x, box_y, box_w, box_h), border_radius=20
    )
    pygame.draw.rect(
        screen, CORES["titulo"], (box_x, box_y, box_w, box_h), width=3, border_radius=20
    )

    # Barra de progresso
    prog_w = box_w - 50
    prog_h = 12
    prog_x = box_x + 25
    prog_y = box_y + 50
    proporcao = indice / total if total > 0 else 0
    pygame.draw.rect(
        screen, CORES["cinza"], (prog_x, prog_y, prog_w, prog_h), border_radius=6
    )
    pygame.draw.rect(
        screen,
        CORES["verde"],
        (prog_x, prog_y, int(prog_w * proporcao), prog_h),
        border_radius=6,
    )

    # Título e pontuação
    fonte_tit = carregar_fonte("upheavtt.ttf", sf(24))
    tit = fonte_tit.render(" PERGUNTA", True, CORES["titulo"])
    screen.blit(tit, (box_x + 25, box_y + 20))
    fonte_score = carregar_fonte("upheavtt.ttf", sf(20))
    score_txt = fonte_score.render(f" {pontuacao}/{total}", True, CORES["titulo"])
    screen.blit(score_txt, (box_x + box_w - score_txt.get_width() - 25, box_y + 22))

    # Disciplina e dificuldade
    disc = pergunta.get("disciplina", "Geral")[:25]
    diff = pergunta.get("dificuldade", pergunta.get("nivel", "Médio"))[:15]
    fonte_info = carregar_fonte("upheavtt.ttf", sf(16))
    info = fonte_info.render(f"{disc}  |  {diff}", True, CORES["destaque"])
    screen.blit(info, (box_x + 28, prog_y + 25))

    # Linha separadora
    separador_y = prog_y + 55
    pygame.draw.line(
        screen,
        CORES["titulo"],
        (box_x + 25, separador_y),
        (box_x + box_w - 25, separador_y),
        2,
    )

    # ── Área de conteúdo rolável (pergunta + alternativas) ──────────────────
    conteudo_top = separador_y + 15
    conteudo_bottom = box_y + box_h - 50  # deixa espaço pra instrução embaixo
    conteudo_rect = pygame.Rect(
        box_x, conteudo_top, box_w, conteudo_bottom - conteudo_top
    )
    quiz_conteudo_rect = conteudo_rect  # guarda pra checar clique dentro da área visível

    # Pergunta (com quebra de linha)
    texto_pergunta = pergunta.get("pergunta", "Pergunta não disponível")[:300]
    fonte_perg = carregar_fonte("upheavtt.ttf", sf(18))

    def quebrar_texto(texto, fonte, larg_max):
        palavras = texto.split()
        linhas = []
        linha = ""
        for p in palavras:
            teste = linha + " " + p if linha else p
            if fonte.size(teste)[0] <= larg_max:
                linha = teste
            else:
                if linha:
                    linhas.append(linha)
                linha = p
        if linha:
            linhas.append(linha)
        return linhas if linhas else [texto[:60]]

    larg_max_perg = box_w - 60
    linhas_perg = quebrar_texto(texto_pergunta, fonte_perg, larg_max_perg)

    # Alternativas
    opcoes = []
    chaves = ["opcao_a", "opcao_b", "opcao_c", "opcao_d", "opcao_e"]
    chaves_acento = ["opçao_a", "opçao_b", "opçao_c", "opçao_d", "opçao_e"]
    letras = ["A", "B", "C", "D", "E"]
    for i, chave in enumerate(chaves):
        texto = pergunta.get(chave, "")
        if not texto and i < len(chaves_acento):
            texto = pergunta.get(chaves_acento[i], "")
        if texto and len(str(texto)) > 1:
            opcoes.append((letras[i], str(texto)[:120]))
    if not opcoes:
        opcoes = [
            ("A", "Alternativa A"),
            ("B", "Alternativa B"),
            ("C", "Alternativa C"),
        ]

    # Altura total do conteúdo (pergunta + espaço + alternativas)
    altura_pergunta = len(linhas_perg[:5]) * 30 + 20
    altura_alternativas = len(opcoes[:5]) * 48
    altura_total = altura_pergunta + altura_alternativas

    # Calcula scroll máximo e aplica clamp na global
    quiz_max_scroll = max(0, altura_total - conteudo_rect.height)
    quiz_scroll = max(0, min(quiz_scroll, quiz_max_scroll))

    # Recorta a tela pra não desenhar fora da caixa
    clip_anterior = screen.get_clip()
    screen.set_clip(conteudo_rect)

    y_perg = conteudo_top - quiz_scroll
    for i, linha in enumerate(linhas_perg[:5]):
        render = fonte_perg.render(linha, True, CORES["texto"])
        screen.blit(render, (box_x + 30, y_perg + i * 30))

    fonte_alt = carregar_fonte("upheavtt.ttf", sf(16))
    y_alt = y_perg + altura_pergunta
    mouse_pos = pygame.mouse.get_pos()

    # Limpa a lista de retângulos clicáveis e recalcula a cada frame
    quiz_alt_rects = []

    for i, (letra, texto) in enumerate(opcoes[:5]):
        alt_rect = pygame.Rect(box_x + 25, y_alt + i * 48, box_w - 50, 42)
        # Guarda (letra minúscula, rect) pra detecção de clique no loop de eventos
        quiz_alt_rects.append((letra.lower(), alt_rect))

        hover = alt_rect.collidepoint(mouse_pos) and conteudo_rect.collidepoint(mouse_pos)
        cor_fundo = CORES["box_alt"] if hover else (55, 55, 75)
        pygame.draw.rect(screen, cor_fundo, alt_rect, border_radius=12)
        cor_borda = CORES["verde"] if hover else CORES["destaque"]
        largura_borda = 2 if hover else 1
        pygame.draw.rect(screen, cor_borda, alt_rect, width=largura_borda, border_radius=12)
        # Letra
        letra_rect = pygame.Rect(alt_rect.x + 12, alt_rect.y + 8, 28, 26)
        pygame.draw.rect(screen, CORES["titulo"], letra_rect, border_radius=6)
        letra_surf = fonte_alt.render(letra, True, CORES["bg"])
        screen.blit(letra_surf, (letra_rect.x + 8, letra_rect.y + 4))
        # Texto
        texto_render = fonte_alt.render(texto, True, CORES["texto"])
        screen.blit(texto_render, (alt_rect.x + 55, alt_rect.y + 12))

    # Restaura o clip
    screen.set_clip(clip_anterior)

    # Barra de scroll lateral, só aparece se precisar rolar
    if quiz_max_scroll > 0:
        barra_x = conteudo_rect.right - 6
        barra_altura = max(
            20, conteudo_rect.height * conteudo_rect.height / altura_total
        )
        proporcao_scroll = quiz_scroll / quiz_max_scroll
        barra_y = conteudo_rect.top + proporcao_scroll * (
            conteudo_rect.height - barra_altura
        )
        pygame.draw.rect(
            screen,
            CORES["cinza"],
            (barra_x, conteudo_rect.top, 5, conteudo_rect.height),
            border_radius=3,
        )
        pygame.draw.rect(
            screen, CORES["destaque"], (barra_x, barra_y, 5, barra_altura), border_radius=3
        )

    # Instrução
    fonte_inst = carregar_fonte("upheavtt.ttf", sf(14))
    instrucao = fonte_inst.render(
        "Clique ou use A B C D E / 1 2 3 4 5 = Responder   |   ESC = Voltar",
        True,
        CORES["destaque"],
    )
    screen.blit(instrucao, instrucao.get_rect(center=(W // 2, box_y + box_h - 25)))

    # Mensagem de feedback
    if mensagem and tempo_msg > 0:
        fonte_msg = carregar_fonte("upheavtt.ttf", sf(28))
        cor_msg = CORES["verde"] if "ACERTOU" in mensagem else CORES["vermelho"]
        msg_surf = fonte_msg.render(mensagem, True, cor_msg)
        msg_bg = pygame.Surface(
            (msg_surf.get_width() + 40, msg_surf.get_height() + 20), pygame.SRCALPHA
        )
        msg_bg.fill((0, 0, 0, 200))
        msg_x = (W - msg_bg.get_width()) // 2
        msg_y = H - 90
        screen.blit(msg_bg, (msg_x, msg_y))
        screen.blit(msg_surf, (msg_x + 20, msg_y + 10))

    return mouse_pos


# ── Intro do personagem ─────────────────────────────────────────────────────
intro_personagem_img = None
intro_personagem_rect = None
intro_personagem_x = -200
intro_personagem_y = 0
intro_velocidade = 3
intro_animacao_finalizada = False
intro_frames = []
intro_frame_index = 0
intro_frame_counter = 0
intro_frame_delay = 12

# Balão de fala: índice da fala atual (-1 = nenhuma)
intro_indice_fala = -1

texto_historia = [
    "Bem-vindo ao I.S.A!",
    "Ajude a personagem a coletar os minerios",
    "e responder as perguntas.",
    "Clique em qualquer lugar para continuar.",
]


def inicializar_intro():
    global intro_personagem_img, intro_personagem_rect
    global intro_personagem_x, intro_personagem_y
    global intro_animacao_finalizada, intro_frames
    global intro_frame_index, intro_frame_counter
    global intro_indice_fala

    frame_names = [
        "S4.png",
        "S5.png",
    ]

    intro_frames = []
    for nome in frame_names:
        try:
            sprite = carregar_imagem("personagens", nome)
            intro_frames.append(pygame.transform.scale(sprite, (135, 220)))
        except:
            continue
    if not intro_frames:
        try:
            fallback = carregar_imagem("personagens", "Areninha4 2.png")
            intro_frames = [pygame.transform.scale(fallback, (220, 220))]
        except:
            intro_frames = []

    intro_frame_index = 0
    intro_frame_counter = 0
    intro_indice_fala = -1  # nenhum balão ainda
    intro_personagem_img = intro_frames[0] if intro_frames else None
    intro_personagem_x = -140
    intro_personagem_y = constants.SCREEN_HEIGHT - 250
    intro_personagem_rect = (
        intro_personagem_img.get_rect(topleft=(intro_personagem_x, intro_personagem_y))
        if intro_personagem_img
        else None
    )
    intro_animacao_finalizada = False


def atualizar_intro():
    """Avança a animação de corrida. Chamar apenas quando estado == 'INTRO'."""
    global intro_personagem_x, intro_personagem_rect
    global intro_frame_index, intro_frame_counter
    global intro_personagem_img, intro_animacao_finalizada, intro_indice_fala

    destino_x = sx(50)
    if intro_personagem_x < destino_x:
        intro_personagem_x += intro_velocidade
        if intro_personagem_rect:
            intro_personagem_rect.x = intro_personagem_x
        intro_frame_counter += 1
        if intro_frame_counter >= intro_frame_delay:
            intro_frame_counter = 0
            if intro_frames:
                intro_frame_index = (intro_frame_index + 1) % len(intro_frames)
                intro_personagem_img = intro_frames[intro_frame_index]
    else:
        if not intro_animacao_finalizada:
            intro_animacao_finalizada = True
            intro_indice_fala = 0
            try:
                sprite_parado = carregar_imagem("personagens", "S7.png")
                intro_personagem_img = pygame.transform.scale(sprite_parado, (220, 220))
            except:
                pass


def processar_clique_intro(pos_mouse):
    global intro_indice_fala, estado_jogo

    if not intro_animacao_finalizada:
        return
    if not intro_personagem_rect:
        return

    if not intro_personagem_rect.collidepoint(pos_mouse):
        return

    intro_indice_fala = (intro_indice_fala + 1) % len(texto_historia)


def desenhar_intro(mouse_pos):
    W, H = constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT

    # Personagem
    if intro_personagem_img and intro_personagem_rect:
        screen.blit(intro_personagem_img, intro_personagem_rect)

        # ── Balão de fala ───────────────────────────────────────────
        if intro_animacao_finalizada and 0 <= intro_indice_fala < len(texto_historia):
            fala = texto_historia[intro_indice_fala]
            fonte_b = carregar_fonte("upheavtt.ttf", sf(18))
            surf_txt = fonte_b.render(fala, True, (20, 20, 20))
            pad = 12
            bal_w = surf_txt.get_width() + pad * 2
            bal_h = surf_txt.get_height() + pad * 2 + 22
            bal_x = intro_personagem_rect.right + sx(14)
            bal_y = intro_personagem_rect.top

            # Garante que não sai da tela pela direita
            if bal_x + bal_w > W - 10:
                bal_x = intro_personagem_rect.left - bal_w - sx(14)

            # Fundo branco do balão
            pygame.draw.rect(
                screen, (255, 255, 240), (bal_x, bal_y, bal_w, bal_h), border_radius=12
            )
            pygame.draw.rect(
                screen, (80, 60, 20), (bal_x, bal_y, bal_w, bal_h), 2, border_radius=12
            )

            # Rabinho do balão (triângulo apontando para o personagem)
            cx = bal_x  # borda esquerda do balão
            cy = bal_y + bal_h // 2
            pygame.draw.polygon(
                screen,
                (255, 255, 240),
                [
                    (cx, cy - 8),
                    (cx, cy + 8),
                    (cx - sx(12), cy),
                ],
            )
            pygame.draw.lines(
                screen,
                (80, 60, 20),
                False,
                [
                    (cx, cy - 8),
                    (cx - sx(12), cy),
                    (cx, cy + 8),
                ],
                2,
            )

            screen.blit(surf_txt, (bal_x + pad, bal_y + pad))
            # instrução de continuar
            fonte_inst = carregar_fonte("upheavtt.ttf", sf(13))
            inst = fonte_inst.render("[ clique para continuar ]", True, (120, 100, 40))
            screen.blit(inst, (bal_x + pad, bal_y + bal_h - inst.get_height() - 4))

            # Contador de falas (ex: 1/4)
            prog = fonte_titulo.render(
                f"{intro_indice_fala + 1}/{len(texto_historia)}", True, constants.YELLOW
            )
            screen.blit(
                prog,
                (
                    bal_x + bal_w - prog.get_width() - 6,
                    bal_y + bal_h - prog.get_height() - 4,
                ),
            )


def abrir_historia():
    global estado_jogo
    estado_jogo = "HISTORIA"


# ── Variáveis de jogo ─────────────────────────────────────────────────────────
player = None
world = None
enemies = []
itens = []
camera_x = 0
camera_y = 0
moving_left = moving_right = False
jump_pressed = False

perguntas = []
pontuacao = 0
indice = 0
quiz_mensagem = ""
quiz_timer = 0
item_para_remover = None
quiz_scroll = 0          # posição atual do scroll na tela de perguntas
quiz_max_scroll = 0      # limite máximo de scroll (calculado a cada frame)
quiz_alt_rects = []      # lista de (letra_minuscula, pygame.Rect) das alternativas desenhadas no frame atual
quiz_conteudo_rect = None  # área visível (recortada) do conteúdo, pra validar cliques


def reiniciar_movimento():
    global moving_left, moving_right, jump_pressed
    moving_left = moving_right = jump_pressed = False


def carregar_perguntas():
    try:
        lista = carregar_perguntas_csv("perguntas.csv")
        if lista:
            print(f" {len(lista)} perguntas carregadas")
            return lista
    except Exception as e:
        print(f"Erro ao carregar perguntas: {e}")
    # Fallback
    print(" Usando perguntas padrão")

    # NÃO CONSERTE ESSA IDENTAÇÃO, O CÓDIGO QUEBRA SE FIZER ISSO (Guilherme)
    return [
        {
            "disciplina": "Teste",
            "dificuldade": "Fácil",
            "pergunta": "Quanto é 2+2?",
            "opcao_a": "3",
            "opcao_b": "4",
            "opcao_c": "5",
            "opcao_d": "6",
            "opcao_e": "",
            "resposta": "b",
        },
        {
            "disciplina": "Teste",
            "dificuldade": "Fácil",
            "pergunta": "Qual a cor do céu?",
            "opcao_a": "Verde",
            "opcao_b": "Azul",
            "opcao_c": "Vermelho",
            "opcao_d": "Amarelo",
            "opcao_e": "",
            "resposta": "b",
        },
    ]


perguntas = carregar_perguntas()


# ── Processa uma resposta (chamada tanto pelo teclado quanto pelo clique) ─────
def processar_resposta(resposta):
    global pontuacao, quiz_mensagem, quiz_timer, indice, quiz_scroll
    global item_para_remover, estado_jogo

    if not resposta or indice >= len(perguntas):
        return

    gabarito = perguntas[indice].get("resposta", "").strip().lower()
    if resposta == gabarito:
        pontuacao += 1
        quiz_mensagem = "VOCE ACERTOU! +20 de vida"
        if player and player.alive:
            player.player_health = min(
                player.player_health + 20, constants.PLAYER_HEALTH
            )
    else:
        quiz_mensagem = "VOCE ERROU!"
        if player and player.alive:
            player.player_health -= constants.DAMAGE
            if player.player_health <= 0:
                player.player_health = 0
                player.alive = False

    quiz_timer = 90
    indice += 1
    quiz_scroll = 0  # reseta o scroll pra próxima pergunta
    reiniciar_movimento()
    if item_para_remover and item_para_remover in itens:
        itens.remove(item_para_remover)
    item_para_remover = None
    estado_jogo = "QUIZ_FEEDBACK"


# ── Carregamento do nível ─────────────────────────────────────────────────────
def carregar_recursos_jogo():
    global player, world, enemies, itens, camera_x, camera_y
    global moving_left, moving_right, jump_pressed
    global pontuacao, indice, quiz_mensagem, quiz_timer, item_para_remover
    tela_carregamento(screen, 0.2, "Carregando tiles...")
    tile_surface = carregar_tile("tile_brick.png", constants.TILE_SIZE)
    tile_list = [tile_surface] * constants.TILE_TYPES
    world_data = carregar_nivel_csv("level1_data.csv")
    tela_carregamento(screen, 0.4, "Construindo mundo...")
    world = World()
    world.process_data(world_data, tile_list)
    tela_carregamento(screen, 0.6, "Carregando personagem...")
    player_image = carregar_imagem("personagens", "areninha_ISA.png")
    player = Character(
        constants.PLAYER_START_X,
        constants.PLAYER_START_Y,
        # NÃO CONSERTE ESSA IDENTAÇÃO, O CÓDIGO QUEBRA SE FIZER ISSO (Guilherme)
        constants.PLAYER_SIZE,
        constants.PLAYER_SPEED,
        player_image,
        constants.PLAYER_HEALTH,
    )
    tela_carregamento(screen, 0.8, "Carregando inimigos e itens...")
    enemies = [Enemy(x=constants.PLAYER_START_X + 300, y=constants.PLAYER_START_Y)]
    # Minérios posicionados em cima dos tiles sólidos reais do level1_data.csv
    # Calculado dinamicamente lendo o topo da primeira tile sólida de cada coluna.
    # TILE_SIZE = 80px; minério tem 40x40px e fica centralizado acima do tile.
    MINERIO_H = 40
    MINERIO_W = 40
    TILE = constants.TILE_SIZE  # 80px

    def _topo_tile_em_col(world_data, col_idx):
        """Retorna y_pixel do topo do tile sólido mais alto na coluna, ou None."""
        SOLID_IDS = {0, 6, 7}
        for row_idx, row in enumerate(world_data):
            if col_idx < len(row) and row[col_idx] in SOLID_IDS:
                return row_idx * TILE
        return None

    world_data = carregar_nivel_csv("level1_data.csv")

    # Colunas escolhidas para distribuir os minérios (índice de coluna no CSV)
    colunas_minerios = [7, 10, 14, 18, 22, 26, 30, 33, 37, 42]

    posicoes_minerios = []
    for col_idx in colunas_minerios:
        y_topo = _topo_tile_em_col(world_data, col_idx)
        if y_topo is not None:
            px = col_idx * TILE + (TILE - MINERIO_W) // 2  # centralizado no tile
            py = y_topo - MINERIO_H  # logo acima do bloco
            posicoes_minerios.append((px, py))
    itens = [
        minerio_cobre("m_minerio.png", x=px, y=py, tamanho=(40, 40))
        for px, py in posicoes_minerios
    ]
    camera_x = camera_y = 0
    reiniciar_movimento()
    pontuacao = 0
    indice = 0
    quiz_mensagem = ""
    quiz_timer = 0
    item_para_remover = None
    tela_carregamento(screen, 1.0, "Pronto!")
    pygame.time.wait(300)


# ── Câmera ────────────────────────────────────────────────────────────────────
def atualizar_camera():
    global camera_x, camera_y
    target_x = player.rect.centerx - constants.SCREEN_WIDTH // 2
    target_y = player.rect.centery - constants.SCREEN_HEIGHT // 2
    map_w = constants.MAP_COLS * constants.TILE_SIZE
    map_h = constants.MAP_ROWS * constants.TILE_SIZE
    camera_x = max(0, min(target_x, map_w - constants.SCREEN_WIDTH))
    camera_y = max(0, min(target_y, map_h - constants.SCREEN_HEIGHT))


# ── Ações dos botões ──────────────────────────────────────────────────────────
def iniciar_jogo():
    global estado_jogo
    if perguntas:
        random.shuffle(perguntas)
    carregar_recursos_jogo()
    estado_jogo = "JOGANDO"


def encerrar_jogo():
    pygame.quit()
    sys.exit()


def abrir_login():
    global estado_jogo
    estado_jogo = "LOGIN"
    print("Login não implementado")


def abrir_historia():
    global estado_jogo
    estado_jogo = "HISTORIA"


def configurar_jogo():
    global estado_jogo
    estado_jogo = "CONFIGURACOES"


def retomar_jogo():
    global estado_jogo
    estado_jogo = "JOGANDO"


def voltar_menu():
    global estado_jogo, player, world, enemies, itens
    player = world = None
    enemies = []
    itens = []
    estado_jogo = "MENU"


def abrir_creditos():
    global estado_jogo
    estado_jogo = "CREDITOS"


# ── Loop principal ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    pygame.init()
    try:
        mixer.init()
    except:
        print("Mixer não inicializado")
    screen = pygame.display.set_mode((BASE_W, BASE_H))
    pygame.display.set_caption("I.S.A - Intelligent Support Agent")
    clock = pygame.time.Clock()
    constants.SCREEN_WIDTH = screen.get_width()
    constants.SCREEN_HEIGHT = screen.get_height()
    tela_carregamento(screen, 0.0, "Inicializando...")
    pygame.display.flip()

    recriar_ui()
    inicializar_intro()

    tela_login = TelaLogin(screen)
    tela_configuracoes = TelaConfiguracoes(
        screen,
        constants.SCREEN_WIDTH,
        constants.SCREEN_HEIGHT,
        callback_voltar=voltar_menu,
        callback_creditos=abrir_creditos,
    )

    # Mapa de teclas de letra -> resposta (além dos números 1-5)
    TECLAS_LETRA = {
        pygame.K_a: "a",
        pygame.K_b: "b",
        pygame.K_c: "c",
        pygame.K_d: "d",
        pygame.K_e: "e",
    }
    TECLAS_NUMERO = {
        pygame.K_1: "a",
        pygame.K_2: "b",
        pygame.K_3: "c",
        pygame.K_4: "d",
        pygame.K_5: "e",
    }

    run = True
    while run:
        clock.tick(constants.FPS)
        mouse_pos = pygame.mouse.get_pos()
        if quiz_timer > 0:
            quiz_timer -= 1
            if quiz_timer == 0 and estado_jogo not in ("QUIZ_FEEDBACK", "QUIZ"):
                quiz_mensagem = ""

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
                if screen.get_flags() & pygame.FULLSCREEN:
                    screen = pygame.display.set_mode((BASE_W, BASE_H))
                else:
                    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT = (
                    screen.get_width(),
                    screen.get_height(),
                )
                recriar_ui()
                inicializar_intro()
                tela_login = TelaLogin(screen, voltar_menu)
                tela_login.redimensionar(
                    constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT
                )

                tela_configuracoes = TelaConfiguracoes(
                    screen,
                    constants.SCREEN_WIDTH,
                    constants.SCREEN_HEIGHT,
                    callback_voltar=voltar_menu,
                    callback_creditos=abrir_creditos,
                    callback_toggle_fullscreen=lambda: None,
                )

                tela_creditos = TelaCreditos(
                    screen,
                    constants.SCREEN_WIDTH,
                    constants.SCREEN_HEIGHT,
                    callback_voltar=voltar_menu,
                )

            elif estado_jogo == "MENU":
                for botao in botoes_menu:
                    botao.verificar_click(event)
                if (
                    event.type == pygame.MOUSEBUTTONDOWN and event.button == 1
                ):  # ← linha nova
                    processar_clique_intro(event.pos)  # ← linha nova
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
                if event.type == pygame.MOUSEWHEEL:
                    quiz_scroll -= event.y * 25
                    quiz_scroll = max(0, min(quiz_scroll, quiz_max_scroll))

                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    # Clique numa alternativa: só conta se estiver dentro da
                    # área visível (recortada) do conteúdo, senão dá pra
                    # "clicar" numa alternativa escondida pelo scroll.
                    if quiz_conteudo_rect and quiz_conteudo_rect.collidepoint(event.pos):
                        for letra, alt_rect in quiz_alt_rects:
                            if alt_rect.collidepoint(event.pos):
                                processar_resposta(letra)
                                break

                elif event.type == pygame.KEYDOWN:
                    resposta = TECLAS_NUMERO.get(event.key) or TECLAS_LETRA.get(
                        event.key
                    )
                    if resposta:
                        processar_resposta(resposta)

            elif estado_jogo == "PAUSADO":
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    estado_jogo = "JOGANDO"
                for botao in botoes_pausa:
                    botao.verificar_click(event)
            elif estado_jogo == "GAME_OVER":
                for botao in botoes_game_over:
                    botao.verificar_click(event)
            elif estado_jogo == "QUIZ_FEEDBACK":
                pass
            elif estado_jogo == "HISTORIA":
                if event.type in (pygame.MOUSEBUTTONDOWN, pygame.KEYDOWN):
                    voltar_menu()
            elif estado_jogo == "LOGIN":
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    for botao in botoes_menu:
                        botao.verificar_click(event)
                    estado_jogo = "MENU"
            elif estado_jogo == "CONFIGURACOES":
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    estado_jogo = "MENU"
                tela_configuracoes.handle_event(event)
            elif estado_jogo == "CREDITOS":
                tela_creditos.handle_event(event)

        # Atualização
        if estado_jogo == "MENU":
            atualizar_intro()
        elif estado_jogo == "JOGANDO" and player:
            if jump_pressed:
                if player.jump():
                    jump_pressed = False
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
            if (
                not player.alive
                or player.rect.top > constants.MAP_ROWS * constants.TILE_SIZE
            ):
                estado_jogo = "GAME_OVER"

        if estado_jogo == "QUIZ_FEEDBACK" and quiz_timer == 0:
            if player and not player.alive:
                estado_jogo = "GAME_OVER"
            else:
                estado_jogo = "JOGANDO"
            quiz_mensagem = ""

        # Renderização
        W, H = constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT
        if estado_jogo == "MENU":
            screen.blit(background_img, (0, 0))
            titulo = fonte_titulo.render("I . S . A", True, constants.YELLOW)
            screen.blit(titulo, titulo.get_rect(center=(W // 2, sy(120))))
            for botao in botoes_menu:
                botao.desenhar(screen, mouse_pos)
            desenhar_intro(mouse_pos)  # ← personagem por cima dos botões
        elif estado_jogo in ("JOGANDO", "PAUSADO"):
            desenhar_paralaxe(camera_x)
            if world:
                world.render(screen, camera_x, camera_y)
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
                BAR_W = sx(200)
                BAR_H = sy(18)
                BAR_X = sx(10)
                BAR_Y = sy(35)
                proporcao = max(
                    0, min(1, player.player_health / constants.PLAYER_HEALTH)
                )
                pygame.draw.rect(
                    screen, constants.RED, (BAR_X, BAR_Y, BAR_W, BAR_H), border_radius=4
                )
                pygame.draw.rect(
                    screen,
                    constants.GREEN,
                    (BAR_X, BAR_Y, int(BAR_W * proporcao), BAR_H),
                    border_radius=4,
                )
                pygame.draw.rect(
                    screen,
                    constants.WHITE,
                    (BAR_X, BAR_Y, BAR_W, BAR_H),
                    2,
                    border_radius=4,
                )
                score_surf = fonte_ui.render(
                    f"Pontos: {pontuacao}", True, constants.WHITE
                )
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
            try:
                if indice < len(perguntas):
                    desenhar_pergunta_melhorado(
                        screen,
                        perguntas[indice],
                        pontuacao,
                        indice,
                        len(perguntas),
                        quiz_mensagem,
                        quiz_timer,
                    )
                else:
                    estado_jogo = "JOGANDO"
            except Exception as e:
                print(f"Erro ao desenhar pergunta: {e}")
                estado_jogo = "JOGANDO"
        elif estado_jogo == "QUIZ_FEEDBACK":
            W2, H2 = constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT
            ov = pygame.Surface((W2, H2), pygame.SRCALPHA)
            ov.fill((0, 0, 0, 220))
            screen.blit(ov, (0, 0))
            cor_fb = (76, 175, 80) if "ACERTOU" in quiz_mensagem else (244, 67, 54)
            fonte_fb = carregar_fonte("upheavtt.ttf", sf(32))
            msg_fb = fonte_fb.render(quiz_mensagem, True, cor_fb)
            screen.blit(msg_fb, msg_fb.get_rect(center=(W2 // 2, H2 // 2)))
            fonte_sub = carregar_fonte("upheavtt.ttf", sf(16))
            sub = fonte_sub.render("Voltando ao jogo...", True, (200, 200, 200))
            screen.blit(sub, sub.get_rect(center=(W2 // 2, H2 // 2 + sy(60))))

        elif estado_jogo == "GAME_OVER":
            screen.blit(background_img, (0, 0))
            overlay = pygame.Surface((W, H), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            screen.blit(overlay, (0, 0))
            surf = fonte_ui.render("GAME OVER", True, constants.RED)
            screen.blit(surf, surf.get_rect(center=(W // 2, sy(180))))
            score_surf = fonte_ui.render(
                f"Pontuacao Final: {pontuacao}", True, constants.YELLOW
            )
            screen.blit(score_surf, score_surf.get_rect(center=(W // 2, sy(240))))
            for botao in botoes_game_over:
                botao.desenhar(screen, mouse_pos)
        elif estado_jogo == "HISTORIA":
            screen.fill((15, 15, 15))
            titulo_historia = fonte_ui.render("HISTORIA", True, constants.YELLOW)
            screen.blit(
                titulo_historia, titulo_historia.get_rect(center=(W // 2, sy(120)))
            )
            y_texto = sy(220)
            for linha in texto_historia:
                texto_surface = fonte_titulo.render(linha, True, constants.WHITE)
                screen.blit(
                    texto_surface, texto_surface.get_rect(center=(W // 2, y_texto))
                )
                y_texto += sy(50)
        elif estado_jogo == "LOGIN":
            tela_login.desenhar()
        elif estado_jogo == "CONFIGURACOES":
            tela_configuracoes.desenhar()
        elif estado_jogo == "CREDITOS":
            screen.blit(background_img, (0, 0))
            tela_creditos.update()
            tela_creditos.desenhar()
        pygame.display.update()
    pygame.quit()
