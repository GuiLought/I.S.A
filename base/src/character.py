import pygame
import math

class Character:
    def __init__(self, x, y, size, speed, image):
        self.image = pygame.transform.scale(image, (size, size))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

        self.pos_x = float(x)
        self.pos_y = float(y)
        # -------------------------------------------------------------

        self.speed = speed
        self.size = size
        self.running = False
        self.flip = False

    def move(self, dx, dy):
        self.running = False

        if dx != 0 or dy != 0:
            self.running = True

        if dx < 0:
            self.flip = True
        elif dx > 0:
            self.flip = False

        # Controlar velocidade diagonal
        if dx != 0 and dy != 0:
            # Multiplicar pela constante (raiz de 2 / 2)
            dx = dx * (math.sqrt(2) / 2)
            dy = dy * (math.sqrt(2) / 2)

        # --- Atualiza as variáveis decimais primeiro ---
        self.pos_x += dx
        self.pos_y += dy

        # Depois atualiza o Rect (que arredonda para o inteiro mais próximo)
        self.rect.x = int(self.pos_x)
        self.rect.y = int(self.pos_y)
        # -------------------------------------------------------------

    def draw(self, surface):
        image = pygame.transform.flip(self.image, self.flip, False)
        surface.blit(image, self.rect)