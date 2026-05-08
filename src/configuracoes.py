import pygame
from src.utils import carregar_fonte

PRETO          = (0,   0,   0)
BRANCO         = (255, 255, 255)
AMARELO        = (241, 187, 52)
AMARELO_ESCURO = (196, 140, 25)
CINZA          = (80,  80,  80)
CINZA_CLARO    = (160, 160, 160)
VERMELHO       = (200, 60,  60)


class SliderVolume:
    def __init__(self, x, y, largura, altura=10):
        self.rect      = pygame.Rect(x, y, largura, altura)
        self.valor     = 0.8          # 0.0 → 1.0
        self.arrastando = False

    @property
    def volume(self):
        return self.valor

    def _handle_pos(self):
        return int(self.rect.x + self.valor * self.rect.width)

    def desenhar(self, tela, fonte):
        # trilha
        pygame.draw.rect(tela, CINZA, self.rect, border_radius=5)
        # preenchimento
        fill = pygame.Rect(self.rect.x, self.rect.y,
                           int(self.valor * self.rect.width), self.rect.height)
        pygame.draw.rect(tela, AMARELO, fill, border_radius=5)
        # bolinha
        cx = self._handle_pos()
        cy = self.rect.centery
        pygame.draw.circle(tela, AMARELO_ESCURO, (cx, cy), 10)
        pygame.draw.circle(tela, PRETO,          (cx, cy), 10, 2)
        # label
        label = fonte.render(f"Volume: {int(self.valor * 100)}%", True, BRANCO)
        tela.blit(label, (self.rect.x, self.rect.y - 30))

    def handle_event(self, evento):
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            cx = self._handle_pos()
            cy = self.rect.centery
            if abs(evento.pos[0] - cx) <= 12 and abs(evento.pos[1] - cy) <= 12:
                self.arrastando = True
        elif evento.type == pygame.MOUSEBUTTONUP:
            self.arrastando = False
        elif evento.type == pygame.MOUSEMOTION and self.arrastando:
            rel = evento.pos[0] - self.rect.x
            self.valor = max(0.0, min(1.0, rel / self.rect.width))
            pygame.mixer.music.set_volume(self.valor)


class BotaoToggle:
    """Botão liga/desliga — ex.: Modo Mudo."""
    def __init__(self, texto, x, y, largura, altura, ativo=False):
        self.texto   = texto
        self.rect    = pygame.Rect(x, y, largura, altura)
        self.ativo   = ativo

    def desenhar(self, tela, fonte, mouse_pos):
        cor_fundo = VERMELHO if self.ativo else CINZA
        hover     = self.rect.collidepoint(mouse_pos)
        if hover:
            cor_fundo = tuple(min(c + 30, 255) for c in cor_fundo)

        pygame.draw.rect(tela, cor_fundo, self.rect, border_radius=10)
        pygame.draw.rect(tela, PRETO,    self.rect, 2, border_radius=10)

        estado = "ON" if self.ativo else "OFF"
        label  = fonte.render(f"{self.texto}: {estado}", True, BRANCO)
        tela.blit(label, label.get_rect(center=self.rect.center))

    def handle_event(self, evento):
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            if self.rect.collidepoint(evento.pos):
                self.ativo = not self.ativo
                pygame.mixer.music.set_volume(0 if self.ativo else 0.8)


class BotaoSimples:
    """Botão comum para ações como Créditos, Voltar etc."""
    def __init__(self, texto, x, y, largura, altura, acao=None):
        self.texto  = texto
        self.rect   = pygame.Rect(x, y, largura, altura)
        self.acao   = acao

    def desenhar(self, tela, fonte, mouse_pos):
        cor = AMARELO_ESCURO if self.rect.collidepoint(mouse_pos) else AMARELO
        pygame.draw.rect(tela, cor,   self.rect, border_radius=12)
        pygame.draw.rect(tela, PRETO, self.rect, 3, border_radius=12)
        label = fonte.render(self.texto, True, PRETO)
        tela.blit(label, label.get_rect(center=self.rect.center))

    def handle_event(self, evento):
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            if self.rect.collidepoint(evento.pos) and self.acao:
                self.acao()


class MenuConfiguracoes:
    """
    Submenu de configurações completo.

    Uso:
        menu_cfg = MenuConfiguracoes(screen, largura, altura, voltar_callback)

    No loop principal:
        if estado == "CONFIGURACOES":
            for event in pygame.event.get():
                menu_cfg.handle_event(event)
            menu_cfg.desenhar()
    """

    def __init__(self, screen, largura, altura, callback_voltar, callback_creditos=None):
        self.screen  = screen
        self.largura = largura
        self.altura  = altura

        fonte = carregar_fonte("upheavtt.ttf", 20)
        fonte_titulo = carregar_fonte("upheavtt.ttf", 32)
        self.fonte       = fonte
        self.fonte_titulo = fonte_titulo

        cx = largura // 2

        self.slider_volume = SliderVolume(cx - 150, 220, 300)

        self.toggle_mudo = BotaoToggle(
            "Modo Mudo", cx - 150, 310, 300, 50, ativo=False
        )

        self.btn_creditos = BotaoSimples(
            "CRÉDITOS", cx - 150, 400, 300, 50, acao=callback_creditos
        )

        self.btn_voltar = BotaoSimples(
            "VOLTAR", cx - 150, 480, 300, 50, acao=callback_voltar
        )

        self.widgets = [self.toggle_mudo, self.btn_creditos, self.btn_voltar]

    def handle_event(self, evento):
        self.slider_volume.handle_event(evento)
        for w in self.widgets:
            w.handle_event(evento)

    def desenhar(self):
        overlay = pygame.Surface((self.largura, self.altura), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))

        titulo = self.fonte_titulo.render("CONFIGURAÇÕES", True, AMARELO)
        self.screen.blit(titulo, titulo.get_rect(center=(self.largura // 2, 140)))

        mouse_pos = pygame.mouse.get_pos()
        self.slider_volume.desenhar(self.screen, self.fonte)
        self.toggle_mudo.desenhar(self.screen, self.fonte, mouse_pos)
        self.btn_creditos.desenhar(self.screen, self.fonte, mouse_pos)
        self.btn_voltar.desenhar(self.screen, self.fonte, mouse_pos)