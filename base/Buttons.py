import pygame
import sys

pygame.init()

# Configurações da tela
LARGURA, ALTURA = 800, 600
TELA = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Menu com Botões")
CLOCK = pygame.time.Clock()
FPS = 60

# Cores
BRANCO = (255, 255, 255)
PRETO = (0, 0, 0)
AMARELO = (241, 187, 52)
AMARELO_ESCURO = (196, 140, 25)

# Fonte
fonte_botao = pygame.font.SysFont("consolas", 30, bold=True)


# Classe Botão

class Botao:
    def __init__(self, texto, x, y, largura, altura, acao=None):
        self.texto = texto
        self.rect = pygame.Rect(x, y, largura, altura)
        self.cor_normal = AMARELO
        self.cor_hover = AMARELO_ESCURO
        self.acao = acao  # função que será chamada quando clicar

    def desenhar(self, tela):
        mouse_pos = pygame.mouse.get_pos()
        cor = self.cor_hover if self.rect.collidepoint(mouse_pos) else self.cor_normal

        # Botão
        pygame.draw.rect(tela, cor, self.rect, border_radius=12)
        pygame.draw.rect(tela, PRETO, self.rect, 3, border_radius=12)

        # Texto centralizado
        texto_img = fonte_botao.render(self.texto, True, PRETO)
        texto_rect = texto_img.get_rect(center=self.rect.center)
        tela.blit(texto_img, texto_rect)

    def verificar_click(self, evento):
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            if self.rect.collidepoint(evento.pos):
                if self.acao:
                    self.acao()  # chama a função associada ao botão
