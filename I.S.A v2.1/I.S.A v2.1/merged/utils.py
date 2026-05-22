from pathlib import Path
import csv
import sys
import pygame

# Suporte a executável empacotado (PyInstaller) e execução normal
if getattr(sys, 'frozen', False):
    ROOT = Path(getattr(sys, '_MEIPASS', Path(sys.executable).parent))
else:
    ROOT = Path(__file__).parent

ASSETS_PATH = ROOT / "assets"


def carregar_imagem(pasta_interna, nome_arquivo, escala=None):
    caminho = ASSETS_PATH / "images" / pasta_interna / nome_arquivo
    img = pygame.image.load(str(caminho)).convert_alpha()
    if escala:
        img = pygame.transform.scale(img, escala)
    return img


def carregar_tile(nome_arquivo, tamanho):
    return carregar_imagem("tiles", nome_arquivo, (tamanho, tamanho))


def carregar_fonte(nome_fonte, tamanho):
    caminho = ASSETS_PATH / "fonts" / nome_fonte
    return pygame.font.Font(str(caminho), tamanho)


def carregar_nivel_csv(nome_arquivo):
    caminho = ASSETS_PATH / "levels" / nome_arquivo
    world_data = []
    with open(str(caminho), newline="") as f:
        reader = csv.reader(f)
        for row in reader:
            world_data.append([int(v) for v in row])
    return world_data


def carregar_perguntas_csv(nome_arquivo):
    """
    Lê o CSV de perguntas e retorna lista de dicts com chaves:
    disciplina, nivel, pergunta, opcao_a..e, resposta
    """
    caminho = ASSETS_PATH / "banco de dados" / nome_arquivo
    perguntas = []
    with open(str(caminho), newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            perguntas.append(dict(row))
    return perguntas
