import pygame

# ── Tela ──────────────────────────────────────────────────────────────────────
FPS            = 75
SCREEN_WIDTH   = 800
SCREEN_HEIGHT  = 600

# ── Player ────────────────────────────────────────────────────────────────────
PLAYER_START_X = 500
PLAYER_START_Y = 80
PLAYER_SIZE    = 75
PLAYER_SPEED   = 5
SPEED_JUMP     = 12   # pixels/frame (positivo, aplicado para cima)

# ── Botões ────────────────────────────────────────────────────────────────────
BTN_LARGURA = 200
BTN_ALTURA  = 60
    
# ── Mundo ─────────────────────────────────────────────────────────────────────
SCALE      = 5
TILE_SIZE  = 16 * SCALE   # 80 px
TILE_TYPES = 18

# Dimensões reais do mapa (CSV 150x150)
MAP_ROWS = 150
MAP_COLS = 150

# ── Física ────────────────────────────────────────────────────────────────────
GRAVITY = 0.6

# ── Debug ─────────────────────────────────────────────────────────────────────
DEBUG = False

# ── Cores ─────────────────────────────────────────────────────────────────────
BLACK   = (0,   0,   0)
WHITE   = (255, 255, 255)
YELLOW  = (255, 255, 0)
PINK    = (255, 0,   255)
RED     = (255, 0,   0)
GREEN   = (0,   200, 0)
MENU_BG = (130, 0,   0)
