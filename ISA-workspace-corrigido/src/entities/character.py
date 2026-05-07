import pygame
import math
import constants


class Character:
    def __init__(self, x, y, size, speed, image):
        self.image_normal  = pygame.transform.scale(image, (size, size))
        self.image_flipped = pygame.transform.flip(self.image_normal, True, False)

        self.rect  = self.image_normal.get_rect(topleft=(x, y))
        self.pos_x = float(x)
        self.pos_y = float(y)

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
            

    # ── Renderização ──────────────────────────────────────────────────────────
    def draw(self, surface, camera_x, camera_y):
        image = self.image_flipped if self.flip else self.image_normal
        draw_rect = self.rect.move(-camera_x, -camera_y)
        surface.blit(image, draw_rect)
