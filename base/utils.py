from pathlib import Path
import pygame

# Define a raiz como a pasta onde o utils.py está
ROOT = Path(__file__).parent

# Define o caminho para a pasta de assets (que está dentro de 'base')
ASSETS_PATH = ROOT / "assets"

def carregar_imagem(pasta_interna, nome_arquivo):
    """
    Exemplo de uso: carregar_imagem("personagens", "hero.png")
    Isso vai buscar em: base/assets/images/personagens/hero.png
    """
    caminho = ASSETS_PATH / "images" / pasta_interna / nome_arquivo
    return pygame.image.load(str(caminho)).convert_alpha()

def carregar_fonte(nome_fonte, tamanho):
    """
    Exemplo de uso: carregar_fonte("upheavtt.ttf", 30)
    """
    caminho = ASSETS_PATH / "fonts" / nome_fonte
    return pygame.font.Font(str(caminho), tamanho)