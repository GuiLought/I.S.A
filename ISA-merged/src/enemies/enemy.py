import pygame
import constants


class Enemy:
    """
    Inimigo básico de plataforma.
    - Tem gravidade e colisão com o mundo
    - Patrulha horizontalmente entre dois limites
    - Reverte direção ao bater em parede ou chegar no limite
    - Colide com o player (knockback simples)
    """

    COR          = (200, 0, 0)       # vermelho
    COR_BORDA    = (120, 0, 0)
    LARGURA      = 50
    ALTURA       = 50
    VELOCIDADE   = 2
    ALCANCE      = 150               # pixels de patrulha para cada lado

    def __init__(self, x, y):
        self.rect  = pygame.Rect(x, y, self.LARGURA, self.ALTURA)
        self.pos_x = float(x)
        self.pos_y = float(y)

        self.vel_y     = 0.0
        self.on_ground = False

        self.direcao   = 1           # 1 = direita, -1 = esquerda
        self.origem_x  = float(x)   # centro da rota de patrulha

    # ── Física e IA ──────────────────────────────────────────────────────────
    def update(self, obstacles):
        # Gravidade
        self.vel_y += constants.GRAVITY
        if self.vel_y > 20:
            self.vel_y = 20

        self.on_ground = False
        dx = self.VELOCIDADE * self.direcao

        # Colisão horizontal
        self.pos_x += dx
        self.rect.x = int(self.pos_x)
        for obs in obstacles:
            if self.rect.colliderect(obs):
                if dx > 0:
                    self.rect.right = obs.left
                elif dx < 0:
                    self.rect.left  = obs.right
                self.pos_x   = float(self.rect.x)
                self.direcao *= -1   # inverte ao bater em parede

        # Inverte ao atingir limite de patrulha
        if abs(self.pos_x - self.origem_x) >= self.ALCANCE:
            self.direcao *= -1

        # Colisão vertical
        self.pos_y += self.vel_y
        self.rect.y = int(self.pos_y)
        for obs in obstacles:
            if self.rect.colliderect(obs):
                if self.vel_y > 0:
                    self.rect.bottom = obs.top
                    self.on_ground   = True
                elif self.vel_y < 0:
                    self.rect.top    = obs.bottom
                self.vel_y = 0
                self.pos_y = float(self.rect.y)

    def check_player_collision(self, player):
        """Aplica dano apenas em colisão lateral. Pular por cima não causa dano."""
        if not self.rect.colliderect(player.rect):
            return False

        # Calcula sobreposição vertical: o quanto o player está "de cima"
        player_vindo_de_cima = (
            player.vel_y >= 0 and
            player.rect.bottom <= self.rect.centery
        )

        if player_vindo_de_cima:
            # Player pulou em cima: empurra inimigo para baixo/salta player
            player.vel_y = -8
            return False

        # Colisão lateral: aplica dano se não estiver invulnerável
        if not player.invulnerable:
            player.stunned      = True
            player.wrong_answer = True
            player.apply_damage()

        # Knockback lateral
        if player.rect.centerx < self.rect.centerx:
            player.pos_x -= 12
        else:
            player.pos_x += 12

        return True

    # ── Renderização ─────────────────────────────────────────────────────────
    def draw(self, surface, camera_x, camera_y):
        draw_rect = self.rect.move(-camera_x, -camera_y)
        pygame.draw.rect(surface, self.COR,      draw_rect, border_radius=6)
        pygame.draw.rect(surface, self.COR_BORDA, draw_rect, 3, border_radius=6)
