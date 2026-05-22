import pygame

from utils import carregar_imagem


# ==========================================
# CORES
# ==========================================

AZUL = (70, 100, 220)
AMARELO = (255, 180, 0)
BRANCO = (255, 255, 255)
CINZA = (230, 230, 230)
PRETO = (0, 0, 0)
ESCURO = (30, 30, 30)


# ==========================================
# TELA LOGIN
# ==========================================

class GerenciadorTelas:

    def __init__(self, screen):

        self.screen = screen

        self.W = screen.get_width()
        self.H = screen.get_height()

        # Funcoes de escala
        self.sx = lambda v: int(v * self.W / 800)
        self.sy = lambda v: int(v * self.H / 600)
        self.sf = lambda v: max(8, int(v * min(self.W / 800, self.H / 600)))

        self.font = pygame.font.SysFont(
            "arial",
            self.sf(28),
            bold=True
        )

        self.font_small = pygame.font.SysFont(
            "arial",
            self.sf(18)
        )

        # ==================================
        # BACKGROUNDS
        # ==================================

        self.bg_login = carregar_imagem(
            "backgrounds",
            "fundo_escola.jpg",
            (self.W, self.H)
        )

        self.bg_historia = carregar_imagem(
            "backgrounds",
            "fundoHistoria.png",
            (self.W, self.H)
        )

        self.bg_menu = carregar_imagem(
            "backgrounds",
            "fundoMenu.png",
            (self.W, self.H)
        )

    def redimensionar(self, nova_largura, nova_altura):
        """Atualiza dimensoes quando a tela e redimensionada"""
        self.W = nova_largura
        self.H = nova_altura
        self.sx = lambda v: int(v * self.W / 800)
        self.sy = lambda v: int(v * self.H / 600)
        self.sf = lambda v: max(8, int(v * min(self.W / 800, self.H / 600)))
        
        self.font = pygame.font.SysFont("arial", self.sf(28), bold=True)
        self.font_small = pygame.font.SysFont("arial", self.sf(18))
        
        # Recarregar backgrounds
        self.bg_login = carregar_imagem("backgrounds", "fundo_escola.jpg", (self.W, self.H))
        self.bg_historia = carregar_imagem("backgrounds", "fundoHistoria.png", (self.W, self.H))
        self.bg_menu = carregar_imagem("backgrounds", "fundoMenu.png", (self.W, self.H))

    # ======================================
    # DESENHAR LOGIN
    # ======================================

    def desenhar(self):

        screen = self.screen

        # ==================================
        # FUNDO
        # ==================================

        screen.blit(self.bg_login, (0, 0))

        # Dimensoes da caixa de login (proporcionais)
        box_largura = self.sx(350)
        box_altura = self.sy(350)
        box_x = (self.W - box_largura) // 2
        box_y = (self.H - box_altura) // 2

        # ==================================
        # SOMBRA
        # ==================================

        pygame.draw.rect(
            screen,
            PRETO,
            (box_x + 5, box_y + 5, box_largura, box_altura),
            border_radius=20
        )

        # ==================================
        # CAIXA LOGIN
        # ==================================

        pygame.draw.rect(
            screen,
            AZUL,
            (box_x, box_y, box_largura, box_altura),
            border_radius=20
        )

        # ==================================
        # TOPO LOGIN
        # ==================================

        topo_largura = self.sx(150)
        topo_altura = self.sy(40)
        topo_x = box_x + (box_largura - topo_largura) // 2
        topo_y = box_y - self.sy(20)

        pygame.draw.rect(
            screen,
            PRETO,
            (topo_x + 2, topo_y + 2, topo_largura, topo_altura),
            border_radius=15
        )

        pygame.draw.rect(
            screen,
            AMARELO,
            (topo_x, topo_y, topo_largura, topo_altura),
            border_radius=15
        )

        txt_login = self.font.render(
            "LOGIN",
            True,
            BRANCO
        )

        screen.blit(txt_login, (topo_x + (topo_largura - txt_login.get_width()) // 2, topo_y + self.sy(8)))

        # ==================================
        # LABELS
        # ==================================

        label_rm = self.font.render("RM:", True, BRANCO)
        screen.blit(label_rm, (box_x + self.sx(20), box_y + self.sy(60)))

        label_senha = self.font.render("SENHA:", True, BRANCO)
        screen.blit(label_senha, (box_x + self.sx(20), box_y + self.sy(140)))

        # ==================================
        # INPUTS
        # ==================================

        input_largura = self.sx(260)
        input_altura = self.sy(45)
        input_x = box_x + (box_largura - input_largura) // 2

        # Input RM
        pygame.draw.rect(
            screen,
            PRETO,
            (input_x + 3, box_y + self.sy(93) + 3, input_largura, input_altura),
            border_radius=20
        )

        pygame.draw.rect(
            screen,
            CINZA,
            (input_x, box_y + self.sy(93), input_largura, input_altura),
            border_radius=20
        )

        # Input Senha
        pygame.draw.rect(
            screen,
            PRETO,
            (input_x + 3, box_y + self.sy(173) + 3, input_largura, input_altura),
            border_radius=20
        )

        pygame.draw.rect(
            screen,
            CINZA,
            (input_x, box_y + self.sy(173), input_largura, input_altura),
            border_radius=20
        )

        # ==================================
        # BOTAO ENTRAR
        # ==================================

        btn_largura = self.sx(150)
        btn_altura = self.sy(50)
        btn_x = box_x + (box_largura - btn_largura) // 2
        btn_y = box_y + box_altura - btn_altura - self.sy(30)

        pygame.draw.rect(
            screen,
            PRETO,
            (btn_x + 3, btn_y + 3, btn_largura, btn_altura),
            border_radius=15
        )

        pygame.draw.rect(
            screen,
            AMARELO,
            (btn_x, btn_y, btn_largura, btn_altura),
            border_radius=15
        )

        txt_btn = self.font.render(
            "ENTRAR",
            True,
            BRANCO
        )

        screen.blit(txt_btn, (btn_x + (btn_largura - txt_btn.get_width()) // 2, btn_y + self.sy(12)))

        # ==================================
        # TEXTO FINAL
        # ==================================

        txt_info = self.font_small.render(
            "REGISTRO FUNCIONAL EM BREVE",
            True,
            BRANCO
        )

        screen.blit(txt_info, (box_x + (box_largura - txt_info.get_width()) // 2, box_y + box_altura - self.sy(15)))


# ==========================================
# TELA LOGIN COM BOTAO VOLTAR
# ==========================================

class TelaLogin(GerenciadorTelas):

    def __init__(self, screen, callback_voltar=None):

        super().__init__(screen)

        self.callback_voltar = callback_voltar

        self.botao_voltar = pygame.Rect(
            self.sx(20),
            self.sy(20),
            self.sx(120),
            self.sy(45)
        )

    def redimensionar(self, nova_largura, nova_altura):
        """Atualiza dimensoes quando a tela e redimensionada"""
        super().redimensionar(nova_largura, nova_altura)
        self.botao_voltar = pygame.Rect(
            self.sx(20),
            self.sy(20),
            self.sx(120),
            self.sy(45)
        )

    # ======================================
    # EVENTOS
    # ======================================

    def handle_event(self, evento):

        if evento.type == pygame.MOUSEBUTTONDOWN:

            if self.botao_voltar.collidepoint(evento.pos):

                if self.callback_voltar:

                    self.callback_voltar()


    # ======================================
    # DESENHAR
    # ======================================

    def desenhar(self):

        super().desenhar()

        pygame.draw.rect(
            self.screen,
            (200, 50, 50),
            self.botao_voltar,
            border_radius=10
        )

        txt = self.font_small.render(
            "VOLTAR",
            True,
            BRANCO
        )

        self.screen.blit(
            txt,
            (self.botao_voltar.x + self.sx(30), self.botao_voltar.y + self.sy(12))
        )


# =========================================================
# =========================================================
# =========================================================




# ==========================================
# SLIDER
# ==========================================

class ControleDeslizante:

    def __init__(self, x, y, larg, valor=0.5):
        self.retangulo = pygame.Rect(x, y, larg, 8)
        self.valor = valor
        self.controle_ret = pygame.Rect(
            x + int(valor * larg) - 4,
            y - 4,
            8,
            16
        )
        self.arrastando = False

    def desenhar(self, superficie):
        # Desenha a linha do slider
        for i in range(self.retangulo.width):
            pygame.draw.rect(
                superficie,
                CINZA,
                (self.retangulo.x + i, self.retangulo.y, 1, self.retangulo.height)
            )
        # Desenha o controle
        pygame.draw.rect(superficie, BRANCO, self.controle_ret)
        pygame.draw.rect(superficie, PRETO, self.controle_ret, 1)

    def atualizar(self, evento):
        if evento.type == pygame.MOUSEBUTTONDOWN:
            if self.controle_ret.collidepoint(evento.pos):
                self.arrastando = True
            # Tambem permite clicar diretamente na linha do slider
            elif self.retangulo.collidepoint(evento.pos):
                x = max(self.retangulo.x, min(evento.pos[0], self.retangulo.x + self.retangulo.w))
                self.controle_ret.x = x - self.controle_ret.width // 2
                self.valor = (x - self.retangulo.x) / self.retangulo.w
                self.arrastando = True

        elif evento.type == pygame.MOUSEBUTTONUP:
            self.arrastando = False

        elif evento.type == pygame.MOUSEMOTION and self.arrastando:
            x = max(self.retangulo.x, min(evento.pos[0], self.retangulo.x + self.retangulo.w))
            self.controle_ret.x = x - self.controle_ret.width // 2
            self.valor = (x - self.retangulo.x) / self.retangulo.w


# ==========================================
# TELA CONFIGURACOES
# ==========================================

class TelaConfiguracoes:

    def __init__(
        self,
        screen,
        largura,
        altura,
        callback_voltar=None,
        callback_creditos=None,
        callback_toggle_fullscreen=None
    ):

        self.screen = screen
        self.W = largura
        self.H = altura
        self.callback_voltar = callback_voltar
        self.callback_creditos = callback_creditos
        self.callback_toggle_fullscreen = callback_toggle_fullscreen

        # Configuracoes
        self.volume_musica = 0.7
        self.volume_efeitos = 0.7
        self.tela_cheia = False

        # Funcoes de escala
        self.sx = lambda v: int(v * self.W / 800)
        self.sy = lambda v: int(v * self.H / 600)
        self.sf = lambda v: max(8, int(v * min(self.W / 800, self.H / 600)))

        self._carregar_fontes()
        self._criar_elementos()

        self.scanline = False
        self.pos_scanline = 0
        self.mensagem = ""
        self.mensagem_timer = 0

    def _carregar_fontes(self):
        try:
            self.fonte = pygame.font.Font("assets/fonts/pixel.ttf", self.sf(16))
            self.fonte_negra = pygame.font.Font("assets/fonts/pixel.ttf", self.sf(20))
            self.fonte_titulo = pygame.font.Font("assets/fonts/pixel.ttf", self.sf(32))
        except:
            self.fonte = pygame.font.SysFont("couriernew", self.sf(16))
            self.fonte_negra = pygame.font.SysFont("couriernew", self.sf(20), bold=True)
            self.fonte_titulo = pygame.font.SysFont("couriernew", self.sf(32), bold=True)

    def _criar_elementos(self):
        # Botao Voltar (X no canto)
        self.botao_voltar = pygame.Rect(self.sx(30), self.sy(40), self.sx(48), self.sy(48))
        
        # Sliders (posicoes e tamanhos proporcionais)
        slider_largura = self.sx(250)
        slider_x = self.sx(250)
        
        self.slider_musica = ControleDeslizante(
            slider_x, self.sy(200), slider_largura, self.volume_musica
        )
        self.slider_efeitos = ControleDeslizante(
            slider_x, self.sy(270), slider_largura, self.volume_efeitos
        )
        
        # Botoes
        self.btn_creditos = pygame.Rect(self.sx(50), self.sy(400), self.sx(200), self.sy(40))
        self.btn_fullscreen = pygame.Rect(self.sx(250), self.sy(350), self.sx(140), self.sy(40))

    def redimensionar(self, nova_largura, nova_altura):
        """Atualiza dimensoes quando a tela e redimensionada"""
        self.W = nova_largura
        self.H = nova_altura
        self.sx = lambda v: int(v * self.W / 800)
        self.sy = lambda v: int(v * self.H / 600)
        self.sf = lambda v: max(8, int(v * min(self.W / 800, self.H / 600)))
        
        self._carregar_fontes()
        self._criar_elementos()

    def desenhar_botao(self, texto, retangulo, cor):
        pygame.draw.rect(self.screen, PRETO, (retangulo.x + 3, retangulo.y + 3, retangulo.width, retangulo.height), border_radius=12)
        pygame.draw.rect(self.screen, cor, retangulo, border_radius=12)
        pygame.draw.rect(self.screen, PRETO, retangulo, 2, border_radius=12)
        txt = self.fonte_negra.render(texto, True, BRANCO)
        self.screen.blit(txt, (retangulo.centerx - txt.get_width() // 2, retangulo.centery - txt.get_height() // 2))

    def desenhar_botao_voltar(self):
        pygame.draw.rect(self.screen, CINZA, self.botao_voltar, border_radius=12)
        pygame.draw.rect(self.screen, PRETO, self.botao_voltar, 2, border_radius=12)
        
        # Desenha a seta (X)
        cx = self.botao_voltar.centerx
        cy = self.botao_voltar.centery
        tamanho = self.sx(16)
        
        pygame.draw.line(self.screen, PRETO, (cx - tamanho//2, cy - tamanho//2), (cx + tamanho//2, cy + tamanho//2), self.sx(3))
        pygame.draw.line(self.screen, PRETO, (cx + tamanho//2, cy - tamanho//2), (cx - tamanho//2, cy + tamanho//2), self.sx(3))

    def handle_event(self, evento):
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_s:
                self.scanline = not self.scanline

        if evento.type == pygame.MOUSEBUTTONDOWN:
            if self.botao_voltar.collidepoint(evento.pos):
                if self.callback_voltar:
                    self.callback_voltar()
            
            if self.btn_creditos.collidepoint(evento.pos):
                if self.callback_creditos:
                    self.callback_creditos()

            if self.btn_fullscreen.collidepoint(evento.pos):
                if self.callback_toggle_fullscreen:
                    self.callback_toggle_fullscreen()
                    self.tela_cheia = not self.tela_cheia
                    self.mensagem = "Pressione F11 para alternar o modo de tela!"
                    self.mensagem_timer = 180

        self.slider_musica.atualizar(evento)
        self.slider_efeitos.atualizar(evento)

        # Atualiza os valores
        self.volume_musica = self.slider_musica.valor
        self.volume_efeitos = self.slider_efeitos.valor

        # Timer da mensagem
        if self.mensagem_timer > 0:
            self.mensagem_timer -= 1
            if self.mensagem_timer == 0:
                self.mensagem = ""

    def desenhar(self):
        tela = self.screen
        tela.fill(ESCURO)

        # Painel principal (centralizado e proporcional)
        painel_largura = self.sx(550)
        painel_altura = self.sy(550)
        painel = pygame.Rect(
            self.W // 2 - painel_largura // 2,
            self.sy(50),
            painel_largura,
            painel_altura
        )
        pygame.draw.rect(tela, (40, 40, 60), painel, border_radius=20)
        pygame.draw.rect(tela, AMARELO, painel, 3, border_radius=20)

        # Titulo
        titulo = self.fonte_titulo.render("CONFIGURACOES", True, AMARELO)
        tela.blit(titulo, (painel.centerx - titulo.get_width() // 2, painel.y + self.sy(20)))

        # Margens internas
        margem_x = painel.x + self.sx(30)
        y_atual = painel.y + self.sy(80)
        espacamento = self.sy(50)

        # ===== SECAO AUDIO =====
        titulo_audio = self.fonte_negra.render("AUDIO", True, (100, 200, 255))
        tela.blit(titulo_audio, (margem_x, y_atual))
        y_atual += self.sy(35)

        # Volume da Musica
        label_musica = self.fonte.render("Volume da Musica:", True, BRANCO)
        tela.blit(label_musica, (margem_x, y_atual))
        
        # Recriar slider musica a cada frame com posicao correta
        slider_largura = self.sx(250)
        self.slider_musica.retangulo = pygame.Rect(margem_x + self.sx(200), y_atual + self.sy(5), slider_largura, self.sy(8))
        self.slider_musica.controle_ret = pygame.Rect(
            self.slider_musica.retangulo.x + int(self.slider_musica.valor * slider_largura) - self.sx(4),
            self.slider_musica.retangulo.y - self.sy(4),
            self.sx(8),
            self.sy(16)
        )
        self.slider_musica.desenhar(tela)
        
        # Percentual
        valor_musica = self.fonte.render(f"{int(self.volume_musica * 100)}%", True, AMARELO)
        tela.blit(valor_musica, (self.slider_musica.retangulo.x + self.slider_musica.retangulo.width + self.sx(10), y_atual))
        y_atual += espacamento

        # Volume dos Efeitos
        label_efeitos = self.fonte.render("Volume dos Efeitos:", True, BRANCO)
        tela.blit(label_efeitos, (margem_x, y_atual))
        
        # Recriar slider efeitos a cada frame com posicao correta
        self.slider_efeitos.retangulo = pygame.Rect(margem_x + self.sx(200), y_atual + self.sy(5), slider_largura, self.sy(8))
        self.slider_efeitos.controle_ret = pygame.Rect(
            self.slider_efeitos.retangulo.x + int(self.slider_efeitos.valor * slider_largura) - self.sx(4),
            self.slider_efeitos.retangulo.y - self.sy(4),
            self.sx(8),
            self.sy(16)
        )
        self.slider_efeitos.desenhar(tela)
        
        # Percentual
        valor_efeitos = self.fonte.render(f"{int(self.volume_efeitos * 100)}%", True, AMARELO)
        tela.blit(valor_efeitos, (self.slider_efeitos.retangulo.x + self.slider_efeitos.retangulo.width + self.sx(10), y_atual))
        y_atual += espacamento + self.sy(10)

        # Linha separadora
        pygame.draw.line(tela, AMARELO, (painel.x + self.sx(20), y_atual), (painel.x + painel.width - self.sx(20), y_atual), 2)
        y_atual += self.sy(30)

        # ===== SECAO VIDEO =====
        titulo_video = self.fonte_negra.render("VIDEO", True, (100, 200, 255))
        tela.blit(titulo_video, (margem_x, y_atual))
        y_atual += self.sy(35)

        # Tela Cheia
        label_full = self.fonte.render("Modo Tela Cheia:", True, BRANCO)
        tela.blit(label_full, (margem_x, y_atual))
        
        self.btn_fullscreen = pygame.Rect(margem_x + self.sx(200), y_atual - self.sy(5), self.sx(140), self.sy(40))
        cor_full = (76, 175, 80) if self.tela_cheia else (100, 100, 120)
        self.desenhar_botao("TELA CHEIA" if not self.tela_cheia else "JANELA", self.btn_fullscreen, cor_full)
        y_atual += espacamento

        # Instrucao
        instrucao = self.fonte.render("Pressione F11 para alternar tela cheia", True, (150, 150, 150))
        tela.blit(instrucao, (margem_x, y_atual))
        y_atual += espacamento + self.sy(10)

        # Linha separadora
        pygame.draw.line(tela, AMARELO, (painel.x + self.sx(20), y_atual), (painel.x + painel.width - self.sx(20), y_atual), 2)
        y_atual += self.sy(30)

        # ===== SECAO INFORMACOES =====
        titulo_info = self.fonte_negra.render("INFORMACOES", True, (100, 200, 255))
        tela.blit(titulo_info, (margem_x, y_atual))
        y_atual += self.sy(35)

        # Botao Creditos
        self.btn_creditos = pygame.Rect(margem_x, y_atual, self.sx(200), self.sy(40))
        self.desenhar_botao("CREDITOS", self.btn_creditos, AZUL)

        # Versao
        versao = self.fonte.render("I.S.A - PRÉ-ALPHA VERSION", True, (150, 150, 150))
        tela.blit(versao, (painel.x + painel.width - versao.get_width() - self.sx(20), painel.y + painel.height - self.sy(30)))

        # Botao Voltar (X)
        self.desenhar_botao_voltar()

        # Mensagem de feedback
        if self.mensagem and self.mensagem_timer > 0:
            msg_surf = self.fonte.render(self.mensagem, True, AMARELO)
            msg_rect = msg_surf.get_rect(center=(self.W // 2, self.H - self.sy(50)))
            msg_bg = pygame.Rect(msg_rect.x - self.sx(10), msg_rect.y - self.sy(5), 
                                 msg_rect.width + self.sx(20), msg_rect.height + self.sy(10))
            pygame.draw.rect(tela, PRETO, msg_bg, border_radius=8)
            pygame.draw.rect(tela, AMARELO, msg_bg, 1, border_radius=8)
            tela.blit(msg_surf, msg_rect)

        # Efeito scanline
        if self.scanline:
            self.pos_scanline = (self.pos_scanline + 2) % self.H
            for i in range(0, self.H, 4):
                linha = (self.pos_scanline + i) % self.H
                pygame.draw.line(tela, (0, 0, 0, 50), (0, linha), (self.W, linha), 1)