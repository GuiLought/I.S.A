from pathlib import Path
import csv
import sys
import pygame

# Suporte a executável empacotado (PyInstaller)
if getattr(sys, 'frozen', False):
    ROOT = Path(sys.executable).parent
else:
    ROOT = Path(__file__).parent

ASSETS_PATH = ROOT / "assets"


def carregar_imagem(pasta_interna, nome_arquivo, escala=None):
    """
    Carrega uma imagem de assets/images/<pasta_interna>/<nome_arquivo>.
    Exemplo: carregar_imagem("personagens", "hero.png")
    Exemplo com escala: carregar_imagem("personagens", "hero.png", (64, 64))
    """
    caminho = ASSETS_PATH / "images" / pasta_interna / nome_arquivo
    img = pygame.image.load(str(caminho)).convert_alpha()
    if escala:
        img = pygame.transform.scale(img, escala)
    return img


def carregar_tile(nome_arquivo, tamanho):
    """
    Atalho para carregar e redimensionar um tile de assets/images/tiles/.
    Exemplo: carregar_tile("tile_brick.png", constants.TILE_SIZE)
    """
    return carregar_imagem("tiles", nome_arquivo, (tamanho, tamanho))


def carregar_fonte(nome_fonte, tamanho):
    """
    Carrega uma fonte de assets/fonts/.
    Exemplo: carregar_fonte("upheavtt.ttf", 30)
    """
    caminho = ASSETS_PATH / "fonts" / nome_fonte
    return pygame.font.Font(str(caminho), tamanho)


def carregar_nivel_csv(nome_arquivo):
    """
    Lê um arquivo CSV de assets/levels/ e retorna uma lista 2D de inteiros.
    Exemplo: carregar_nivel_csv("level1_data.csv")
    """
    caminho = ASSETS_PATH / "levels" / nome_arquivo
    world_data = []
    with open(str(caminho), newline="") as f:
        reader = csv.reader(f)
        for row in reader:
            world_data.append([int(v) for v in row])
    return world_data


def carregar_perguntas_csv(nome_arquivo):
    caminho = ASSETS_PATH / "banco de dados" / nome_arquivo
    questions_data = []
    with open(str(caminho), newline="") as f:
        reader = csv.reader(f)
        for row in reader:
            questions_data.append([str(v) for v in row])
    return questions_data
