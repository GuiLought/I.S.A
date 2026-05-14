import pygame
import numpy as np
import constants
from PIL import Image


def _load_spritesheet(path: str, frame_w: int, frame_h: int, num_frames: int, scale: int) -> list:
    """Carrega o sprite sheet, remove fundo escuro e retorna lista de surfaces."""
    pil_img = Image.open(path).convert("RGBA")
    arr = np.array(pil_img, dtype=np.uint8)

    r, g, b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]
    bg_mask = (r < 30) & (g < 30) & (b < 30)
    arr[bg_mask, 3] = 0

    frames = []
    for i in range(num_frames):
        x = i * frame_w
        frame_arr = arr[:, x:x + frame_w, :]
        surf = pygame.image.frombuffer(frame_arr.tobytes(), (frame_w, frame_h), "RGBA").convert_alpha()
        scaled = pygame.transform.scale(surf, (frame_w * scale, frame_h * scale))
        frames.append(scaled)

    return frames


class Character:
    # Configurações do sprite sheet
    FRAME_W    = 80       # largura de cada frame no PNG
    FRAME_H    = 127      # altura de cada frame no PNG
    NUM_FRAMES = 6        # total de frames no sheet
    SCALE      = 1        # fator de escala (ajuste se quiser maior/menor)
    ANIM_SPEED = 100      # ms por frame

    def __init__(self, x, y, size, speed, image, health):
        # Tenta carregar sprite sheet animado; cai de volta para imagem estática
        import os
        sheet_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "assets", "images", "personagens", "areninha_spritesheet.png"
        )

        if os.path.exists(sheet_path):
            self.frames = _load_spritesheet(
                sheet_path, self.FRAME_W, self.FRAME_H, self.NUM_FRAMES, self.SCALE
            )
            self.animated = True
        else:
            # Fallback: usa imagem estática passada
            static = pygame.transform.scale(image, (size, size))
            self.frames = [static]
            self.animated = False

        self.frame_index   = 0
        self.last_anim_time = 0

        # Imagem atual e flipped
        self.image_normal  = self.frames[0]
        self.image_flipped = pygame.transform.flip(self.image_normal, True, False)

        self.rect  = self.image_normal.get_rect(topleft=(x, y))
        self.pos_x = float(x)
        self.pos_y = float(y)

        self.player_health = constants.PLAYER_HEALTH
        self.alive   = True
        self.stunned = False

        self.invulnerable          = False
        self.last_stunned_time     = 0
        self.invulnerable_duration = 1000

        self.wrong_answer = False
        self.right_answer = True

        self.speed     = speed
        self.size      = size
        self.flip      = False
        self.running   = False

        self.vel_y     = 0.0
        self.on_ground = False
        self.jumping   = False

    # ── Animação ──────────────────────────────────────────────────────────────
    def _update_animation(self):
        """Avança o frame de animação se o personagem estiver se movendo."""
        if not self.animated:
            return

        now = pygame.time.get_ticks()
        if self.running and now - self.last_anim_time > self.ANIM_SPEED:
            self.frame_index    = (self.frame_index + 1) % self.NUM_FRAMES
            self.last_anim_time = now
            frame = self.frames[self.frame_index]
            self.image_normal  = frame
            self.image_flipped = pygame.transform.flip(frame, True, False)
        elif not self.running:
            # Parado: volta ao frame 0
            self.frame_index   = 0
            frame = self.frames[0]
            self.image_normal  = frame
            self.image_flipped = pygame.transform.flip(frame, True, False)

    # ── Movimento ─────────────────────────────────────────────────────────────
    def move(self, dx, obstacles):
        self.running = dx != 0

        if dx < 0:
            self.flip = True
        elif dx > 0:
            self.flip = False

        self.vel_y += constants.GRAVITY
        if self.vel_y > 20:
            self.vel_y = 20

        self.on_ground = False

        self.pos_x += dx
        self.rect.x = int(self.pos_x)
        for obs in obstacles:
            if self.rect.colliderect(obs):
                if dx > 0:
                    self.rect.right = obs.left
                elif dx < 0:
                    self.rect.left  = obs.right
                self.pos_x = float(self.rect.x)

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

        self._update_animation()

    def jump(self):
        if self.on_ground:
            self.vel_y     = -constants.SPEED_JUMP
            self.jumping   = True
            self.on_ground = False
            return True
        return False

    def apply_damage(self):
        if self.stunned and self.wrong_answer and not self.invulnerable:
            self.player_health -= constants.DAMAGE
            self.invulnerable      = True
            self.last_stunned_time = pygame.time.get_ticks()
            self.stunned       = False
            self.wrong_answer  = False

            print(f"Dano recebido! Vida restante: {self.player_health}")

            if self.player_health <= 0:
                self.alive         = False
                self.player_health = 0

    def update_invulnerable(self):
        if self.invulnerable:
            current_time = pygame.time.get_ticks()
            if current_time - self.last_stunned_time >= self.invulnerable_duration:
                self.invulnerable = False
                print("Invulnerabilidade terminou - pode tomar dano novamente")

    # ── Renderização ──────────────────────────────────────────────────────────
    def draw(self, surface, camera_x, camera_y):
        if self.invulnerable:
            if pygame.time.get_ticks() % 200 < 100:
                return

        image     = self.image_flipped if self.flip else self.image_normal
        draw_rect = self.rect.move(-camera_x, -camera_y)
        surface.blit(image, draw_rect)
