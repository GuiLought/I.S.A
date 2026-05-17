import pygame
import math
from utils import carregar_fonte

PRETO          = (0,   0,   0)
AMARELO        = (241, 187, 52)
AMARELO_ESCURO = (196, 140, 25)
AZUL           = (40,  60,  200)
CLARO          = (255, 245, 220)


class Botao:
    def __init__(self, texto, x, y, largura, altura, acao=None):
        self.texto      = texto
        self.rect       = pygame.Rect(x, y, largura, altura)
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


class BotaoConfig:
    def __init__(self, cx, cy, raio=35, acao=None):
        self.cx      = cx
        self.cy      = cy
        self.raio    = raio
        self.acao    = acao
        self._angulo = 0.0

    def _dentro(self, pos):
        return (pos[0] - self.cx) ** 2 + (pos[1] - self.cy) ** 2 <= self.raio ** 2

    def _desenhar_engrenagem(self, tela, cor_engrenagem, cor_fundo, dentes=8, offset_ang=0.0):
        cx, cy  = self.cx, self.cy
        inner_r = int(self.raio * 0.55)
        outer_r = int(self.raio * 0.80)

        angle_step = (2 * math.pi) / (dentes * 2)
        points = []
        for i in range(dentes * 2):
            angle = i * angle_step + offset_ang
            r = outer_r if i % 2 == 0 else inner_r
            x = cx + math.cos(angle) * r
            y = cy + math.sin(angle) * r
            points.append((x, y))

        pygame.draw.polygon(tela, cor_engrenagem, points)
        pygame.draw.circle(tela, cor_fundo, (cx, cy), inner_r // 2)

    def desenhar(self, tela, mouse_pos=None):
        if mouse_pos is None:
            mouse_pos = pygame.mouse.get_pos()

        hover = self._dentro(mouse_pos)

        cor_fundo      = AMARELO_ESCURO if hover else AZUL
        cor_engrenagem = AMARELO        if hover else CLARO

        if hover:
            self._angulo += 0.02
        else:
            self._angulo = 0.0

        pygame.draw.circle(tela, cor_fundo, (self.cx, self.cy), self.raio)
        pygame.draw.circle(tela, PRETO, (self.cx, self.cy), self.raio, 2)
        self._desenhar_engrenagem(tela, cor_engrenagem, cor_fundo, offset_ang=self._angulo)

    def verificar_click(self, evento):
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            if self._dentro(evento.pos):
                if self.acao:
                    self.acao()


class BotaoSair:
    def __init__(self, cx, cy, raio=35, acao=None):
        self.cx   = cx
        self.cy   = cy
        self.raio = raio
        self.acao = acao

    def _dentro(self, pos):
        return (pos[0] - self.cx) ** 2 + (pos[1] - self.cy) ** 2 <= self.raio ** 2

    def _desenhar_icone(self, tela, cor_icone):
        cx, cy    = self.cx, self.cy
        espessura = max(3, int(self.raio * 0.13))
        escala    = self.raio / 65

        def s(v):
            return int(v * escala)

        # Corpo em "C"
        pygame.draw.line(tela, cor_icone, (cx + s(28),  cy + s(-32)), (cx + s(-22), cy + s(-32)), espessura)
        pygame.draw.line(tela, cor_icone, (cx + s(-22), cy + s(-32)), (cx + s(-22), cy + s(32)),  espessura)
        pygame.draw.line(tela, cor_icone, (cx + s(-22), cy + s(32)),  (cx + s(28),  cy + s(32)),  espessura)
        # Linha da seta
        pygame.draw.line(tela, cor_icone, (cx + s(-10), cy), (cx + s(32), cy), espessura)
        # Ponta da seta
        pygame.draw.polygon(tela, cor_icone, [
            (cx + s(32), cy),
            (cx + s(18), cy + s(-14)),
            (cx + s(18), cy + s(14)),
        ])

    def desenhar(self, tela, mouse_pos=None):
        if mouse_pos is None:
            mouse_pos = pygame.mouse.get_pos()

        hover = self._dentro(mouse_pos)

        cor_fundo = AMARELO_ESCURO if hover else AZUL
        cor_icone = AMARELO        if hover else CLARO

        pygame.draw.circle(tela, cor_fundo, (self.cx, self.cy), self.raio)
        pygame.draw.circle(tela, PRETO, (self.cx, self.cy), self.raio, 2)
        self._desenhar_icone(tela, cor_icone)

    def verificar_click(self, evento):
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            if self._dentro(evento.pos):
                if self.acao:
                    self.acao()