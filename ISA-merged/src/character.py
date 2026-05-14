import pygame
import math
import constants


class Character:
    def __init__(self, x, y, size, speed, image, health):
        self.image_normal  = pygame.transform.scale(image, (size, size))
        self.image_flipped = pygame.transform.flip(self.image_normal, True, False)

        self.rect  = self.image_normal.get_rect(topleft=(x, y))
        self.pos_x = float(x)
        self.pos_y = float(y)
        
        self.player_health = constants.PLAYER_HEALTH
        self.alive = True
        self.stunned = False
        
        # Invulnerabilidade
        self.invulnerable = False
        self.last_stunned_time = 0  # ← renomeado para clareza
        self.invulnerable_duration = 1000   
        
        self.wrong_answer = False
        self.right_answer = True

        self.speed     = speed
        self.size      = size
        self.flip      = False
        self.running   = False

        # Física vertical
        self.vel_y     = 0.0
        self.on_ground = False
        self.jumping   = False

    # ── Movimento ─────────────────────────────────────────────────────────────
    def move(self, dx, obstacles):
        self.running = dx != 0

        if dx < 0:
            self.flip = True
        elif dx > 0:
            self.flip = False

        # Gravidade
        self.vel_y += constants.GRAVITY
        if self.vel_y > 20:
            self.vel_y = 20

        self.on_ground = False

        # Colisão horizontal
        self.pos_x += dx
        self.rect.x = int(self.pos_x)
        for obs in obstacles:
            if self.rect.colliderect(obs):
                if dx > 0:
                    self.rect.right = obs.left
                elif dx < 0:
                    self.rect.left  = obs.right
                self.pos_x = float(self.rect.x)

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

    def jump(self):
        if self.on_ground:
            self.vel_y     = -constants.SPEED_JUMP
            self.jumping   = True
            self.on_ground = False
            return True
        return False
    
    def apply_damage(self):
    # colisão com inimigo/obstaculo
        if self.stunned and self.wrong_answer and not self.invulnerable:
            self.player_health -= constants.DAMAGE
            self.invulnerable = True
            self.last_stunned_time = pygame.time.get_ticks()
            
            # Reseta os estados após aplicar dano
            self.stunned = False
            self.wrong_answer = False  # ← importante resetar
            
            print(f"Dano recebido! Vida restante: {self.player_health}")
            
            if self.player_health <= 0:
                self.alive = False
                self.player_health = 0

    def update_invulnerable(self):
        """Atualiza o estado de invulnerabilidade - chame no loop principal"""
        if self.invulnerable:
            current_time = pygame.time.get_ticks()
            if current_time - self.last_stunned_time >= self.invulnerable_duration:
                self.invulnerable = False
                print("Invulnerabilidade terminou - pode tomar dano novamente")

    # ── Renderização ──────────────────────────────────────────────────────────
    def draw(self, surface, camera_x, camera_y):
        # Efeito de piscar quando invulnerável (opcional)
        if self.invulnerable:
            # Pisca a cada 100ms
            if pygame.time.get_ticks() % 200 < 100:
                return  # não desenha neste frame
        
        image = self.image_flipped if self.flip else self.image_normal
        draw_rect = self.rect.move(-camera_x, -camera_y)
        surface.blit(image, draw_rect)