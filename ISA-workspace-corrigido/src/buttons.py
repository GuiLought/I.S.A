import pygame
import math
from utils import carregar_fonte

PRETO          = (0,   0,   0)
AMARELO        = (241, 187, 52)
AMARELO_ESCURO = (196, 140, 25)


class Botao:
    def __init__(self, texto, x, y, largura, altura, acao=None, tipo="texto"):
        self.texto      = texto
        self.tipo       = tipo
        self.rect       = pygame.Rect(x, y, largura, altura)
        self.cor_normal = AMARELO
        self.cor_hover  = AMARELO_ESCURO
        self.acao       = acao
        self.fonte      = carregar_fonte("upheavtt.ttf", 20)

    # ── Engrenagem ────────────────────────────────────────────────────────────
    def _desenhar_engrenagem(self, tela, centro, cor, dentes=8):
        cx, cy   = centro
        r_ext    = min(self.rect.width, self.rect.height) // 2 - 4
        r_int    = int(r_ext * 0.72)
        r_furo   = int(r_ext * 0.35)
        passo    = (2 * math.pi) / (dentes * 2)

        pontos = []
        for i in range(dentes * 2):
            angulo = i * passo - math.pi / 2      # começa no topo
            r = r_ext if i % 2 == 0 else r_int
            pontos.append((cx + math.cos(angulo) * r,
                           cy + math.sin(angulo) * r))

        pygame.draw.polygon(tela, cor, pontos)
        pygame.draw.circle(tela, PRETO, centro, r_furo)          # furo central
        pygame.draw.circle(tela, PRETO, centro, r_ext + 2, 2)    # borda externa

    # ── Desenho principal ─────────────────────────────────────────────────────
    def desenhar(self, tela, mouse_pos=None):
        if mouse_pos is None:
            mouse_pos = pygame.mouse.get_pos()

        hover = self.rect.collidepoint(mouse_pos)
        cor   = self.cor_hover if hover else self.cor_normal

        if self.tipo == "texto":
            pygame.draw.rect(tela, cor,   self.rect, border_radius=12)
            pygame.draw.rect(tela, PRETO, self.rect, 3, border_radius=12)
            texto_img  = self.fonte.render(self.texto, True, PRETO)
            texto_rect = texto_img.get_rect(center=self.rect.center)
            tela.blit(texto_img, texto_rect)

        elif self.tipo == "engrenagem":
            # fundo circular
            centro = self.rect.center
            raio   = min(self.rect.width, self.rect.height) // 2
            pygame.draw.circle(tela, cor,   centro, raio)
            self._desenhar_engrenagem(tela, centro, cor)
            # anel de hover
            if hover:
                pygame.draw.circle(tela, PRETO, centro, raio, 3)

    def verificar_click(self, evento):
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            if self.rect.collidepoint(evento.pos):
                if self.acao:
                    self.acao()