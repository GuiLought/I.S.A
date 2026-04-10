import pygame
import math


class Character:
    def __init__(self, x, y, size, speed, image):
        self.image = image
        self.image = pygame.transform.scale(self.image, (size, size))

        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

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

        # controlar velocidade diagonal
        if dx != 0 and dy != 0:
            dx = dx * (math.sqrt(2) / 2)
            dy = dy * (math.sqrt(2) / 2)

        # mover personagem
        self.rect.x += dx
        self.rect.y += dy

    def draw(self, surface):
        image = pygame.transform.flip(self.image, self.flip, False)
        surface.blit(image, self.rect)
