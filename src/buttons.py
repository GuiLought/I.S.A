import pygame
from utils import carregar_fonte

PRETO          = (0,   0,   0)
AMARELO        = (241, 187, 52)
AMARELO_ESCURO = (196, 140, 25)


class Botao:
    def __init__(self, texto, x, y, largura, altura, acao=None):
        self.texto     = texto
        self.rect      = pygame.Rect(x, y, largura, altura)
        self.cor_normal = AMARELO
        self.cor_hover  = AMARELO_ESCURO
        self.acao       = acao
        self.fonte      = carregar_fonte("upheavtt.ttf", 20)

    def desenhar(self, tela, mouse_pos=None):
        if mouse_pos is None:
            mouse_pos = pygame.mouse.get_pos()

        cor = self.cor_hover if self.rect.collidepoint(mouse_pos) else self.cor_normal
        pygame.draw.rect(tela, cor,   self.rect, border_radius=12)
        pygame.draw.rect(tela, PRETO, self.rect, 3, border_radius=12)

        texto_img  = self.fonte.render(self.texto, True, PRETO)
        texto_rect = texto_img.get_rect(center=self.rect.center)
        tela.blit(texto_img, texto_rect)

    def verificar_click(self, evento):
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            if self.rect.collidepoint(evento.pos):
                if self.acao:
                    self.acao()
