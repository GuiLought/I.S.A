import os
import pygame
import numpy as np
import constants
from PIL import Image


def _load_sprite(path: str, target_h: int) -> pygame.Surface:
    """Carrega um sprite PNG, remove fundo escuro (preto), redimensiona mantendo proporção."""
    pil_img = Image.open(path).convert("RGBA")
    w, h = pil_img.size

    arr = np.array(pil_img, dtype=np.uint8)
    r, g, b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]
    # Remove fundo preto
    arr[(r < 30) & (g < 30) & (b < 30), 3] = 0

    # Recorta apenas a região com conteúdo real
    mask = arr[:, :, 3] > 0
    rows = np.where(mask.any(axis=1))[0]
    cols = np.where(mask.any(axis=0))[0]
    if len(rows) == 0 or len(cols) == 0:
        # Imagem vazia — retorna superfície transparente
        surf = pygame.Surface((target_h, target_h), pygame.SRCALPHA)
        return surf

    r0, r1 = rows[0], rows[-1] + 1
    c0, c1 = cols[0], cols[-1] + 1
    cropped = arr[r0:r1, c0:c1]

    crop_h, crop_w = cropped.shape[:2]
    ratio = target_h / crop_h
    target_w = max(1, int(crop_w * ratio))

    pil_crop = Image.fromarray(np.ascontiguousarray(cropped), "RGBA")
    resized = pil_crop.resize((target_w, target_h), Image.NEAREST)
    data = resized.tobytes()
    surf = pygame.image.fromstring(data, (target_w, target_h), "RGBA").convert_alpha()
    return surf


class Character:
    # Dois sprites: [0] parado, [1] andando
    ANIM_SPEED = 200  # ms por frame (alterna entre idle e walk)

    def __init__(self, x, y, size, speed, image, health):
        # Localiza a pasta de personagens
        _bases = [
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            os.getcwd(),
            os.path.join(os.getcwd(), "ISA-merged"),
        ]
        personagens_dir = None
        for _b in _bases:
            _d = os.path.normpath(os.path.join(_b, "assets", "images", "personagens"))
            if os.path.isdir(_d):
                personagens_dir = _d
                break

        self.frames = []
        self.animated = False

        if personagens_dir:
            idle_path = os.path.join(personagens_dir, "Areninha2 1.png")
            walk_path = os.path.join(personagens_dir, "Areninha4 2.png")

            if os.path.exists(idle_path) and os.path.exists(walk_path):
                idle_surf = _load_sprite(idle_path, size)
                walk_surf = _load_sprite(walk_path, size)
                self.frames   = [idle_surf, walk_surf]
                self.animated = True

        if not self.animated:
            # Fallback: usa a imagem genérica passada como argumento
            static = pygame.transform.scale(image, (size, size))
            self.frames   = [static]
            self.animated = False

        self.frame_index    = 0
        self.last_anim_time = 0

        self.image_normal  = self.frames[0]
        self.image_flipped = pygame.transform.flip(self.image_normal, True, False)

        self.rect  = self.image_normal.get_rect(topleft=(x, y))
        self.pos_x = float(x)
        self.pos_y = float(y)

        self.player_health         = constants.PLAYER_HEALTH
        self.alive                 = True
        self.stunned               = False
        self.invulnerable          = False
        self.last_stunned_time     = 0
        self.invulnerable_duration = 1000
        self.wrong_answer          = False
        self.right_answer          = True

        self.speed     = speed
        self.size      = size
        self.flip      = False
        self.running   = False

        self.vel_y     = 0.0
        self.on_ground = False
        self.jumping   = False

    # ── Animação ──────────────────────────────────────────────────────────────
    def _update_animation(self):
        if not self.animated:
            return
        now = pygame.time.get_ticks()

        if self.running and len(self.frames) >= 2:
            # Alterna entre frame idle (0) e walk (1) enquanto se move
            if now - self.last_anim_time > self.ANIM_SPEED:
                self.frame_index    = 1 - (self.frame_index if self.frame_index <= 1 else 0)
                self.last_anim_time = now
        else:
            self.frame_index = 0

        idx = min(self.frame_index, len(self.frames) - 1)
        frame = self.frames[idx]
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
            self.player_health    -= constants.DAMAGE
            self.invulnerable      = True
            self.last_stunned_time = pygame.time.get_ticks()
            self.stunned           = False
            self.wrong_answer      = False
            print(f"Dano recebido! Vida restante: {self.player_health}")
            if self.player_health <= 0:
                self.alive         = False
                self.player_health = 0

    def update_invulnerable(self):
        if self.invulnerable:
            if pygame.time.get_ticks() - self.last_stunned_time >= self.invulnerable_duration:
                self.invulnerable = False
                print("Invulnerabilidade terminou - pode tomar dano novamente")

    # ── Renderização ──────────────────────────────────────────────────────────
    def draw(self, surface, camera_x, camera_y):
        if self.invulnerable and pygame.time.get_ticks() % 200 < 100:
            return
        image     = self.image_flipped if self.flip else self.image_normal
        draw_rect = self.rect.move(-camera_x, -camera_y)
        surface.blit(image, draw_rect)
