import pygame
from utils import carregar_imagem


class minerio_cobre(pygame.sprite.Sprite):
    def __init__(self, nome_arquivo, x, y, tamanho=(40, 40)):
        super().__init__()
        self.image = carregar_imagem("itens", nome_arquivo, tamanho)
        self.rect  = self.image.get_rect(topleft=(x, y))
        self.coletado = False

    def verificar_coleta(self, player):
        if not self.coletado and self.rect.colliderect(player.rect):
            self.coletado = True
            return True
        return False

    def draw(self, surface, camera_x, camera_y):
        if not self.coletado:
            surface.blit(self.image, self.rect.move(-camera_x, -camera_y))