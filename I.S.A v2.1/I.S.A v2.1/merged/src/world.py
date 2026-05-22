import pygame
import constants


# Tiles que são sólidos (colidíveis) — ajuste conforme o design do jogo
SOLID_TILES = {0, 6, 7}


class World:
    def __init__(self):
        self.map_tiles = []   # lista de [Surface, Rect] para renderizar
        self.obstacles = []   # lista de pygame.Rect para colisão

    def process_data(self, data, tile_list):
        """
        Processa a grade 2D de inteiros e monta as listas de tiles e obstáculos.
        tile_list: lista de Surfaces indexada pelo valor do tile.
        Tiles com valor -1 são vazios (ignorados).
        Tiles não mapeados em tile_list usam o primeiro tile como fallback.
        """
        self.map_tiles = []
        self.obstacles  = []

        for y, row in enumerate(data):
            for x, tile_id in enumerate(row):
                if tile_id < 0:
                    continue

                # Fallback: se não houver sprite para o tile_id, usa o índice 0
                idx = tile_id if tile_id < len(tile_list) else 0
                img = tile_list[idx]

                rect = img.get_rect(
                    topleft=(x * constants.TILE_SIZE, y * constants.TILE_SIZE)
                )
                self.map_tiles.append((img, rect))

                if tile_id in SOLID_TILES:
                    self.obstacles.append(rect)

    def render(self, surface, camera_x, camera_y):
        """Desenha apenas os tiles visíveis na tela (culling simples)."""
        screen_rect = pygame.Rect(
            camera_x, camera_y,
            constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT
        )
        for img, rect in self.map_tiles:
            if screen_rect.colliderect(rect):
                surface.blit(img, rect.move(-camera_x, -camera_y))
