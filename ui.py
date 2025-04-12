# ui.py

import pygame

CELL_SIZE = 60
MARGIN = 20
LINE_WIDTH = 8
FONT_SIZE = 24

# Colores predeterminados por número
COLOR_MAP = [
    (255, 0, 0),      # Rojo
    (0, 128, 255),    # Azul
    (0, 200, 0),      # Verde
    (255, 165, 0),    # Naranja
    (128, 0, 128),    # Morado
    (0, 255, 255),    # Cyan
    (255, 192, 203),  # Rosado
    (128, 128, 128),  # Gris
    (255, 255, 0),    # Amarillo
]

def draw_board(screen, board, font):
    screen.fill((255, 255, 255))  # Blanco de fondo

    for r in range(board.rows):
        for c in range(board.cols):
            rect = pygame.Rect(
                MARGIN + c * CELL_SIZE,
                MARGIN + r * CELL_SIZE,
                CELL_SIZE,
                CELL_SIZE
            )
            pygame.draw.rect(screen, (0, 0, 0), rect, 2)  # Borde de celda

            value = board.grid[r][c]
            if value is not None:
                text = font.render(str(value), True, (0, 0, 0))
                text_rect = text.get_rect(center=rect.center)
                screen.blit(text, text_rect)

    for num, path in board.paths.items():
        if len(path) > 1:
            color = COLOR_MAP[(num - 1) % len(COLOR_MAP)]
            points = [
                (MARGIN + c * CELL_SIZE + CELL_SIZE // 2,
                 MARGIN + r * CELL_SIZE + CELL_SIZE // 2)
                for r, c in path
            ]
            pygame.draw.lines(screen, color, False, points, LINE_WIDTH)
