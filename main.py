# main.py

import pygame
from board_parser import read_board_file
from board import Board, is_game_completed
from ui import draw_board, CELL_SIZE, MARGIN, FONT_SIZE

def get_cell_from_mouse(pos):
    x, y = pos
    col = (x - MARGIN) // CELL_SIZE
    row = (y - MARGIN) // CELL_SIZE
    return row, col

def show_menu(screen, font):
    options = ["Jugar manualmente", "Resolver automáticamente"]
    selected = 0

    while True:
        screen.fill((255, 255, 255))
        title = font.render("Seleccione modo de juego", True, (0, 0, 0))
        screen.blit(title, (screen.get_width() // 2 - title.get_width() // 2, 100))

        for i, option in enumerate(options):
            color = (0, 128, 0) if i == selected else (0, 0, 0)
            text = font.render(option, True, color)
            screen.blit(text, (screen.get_width() // 2 - text.get_width() // 2, 200 + i * 50))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected = (selected - 1) % len(options)
                elif event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(options)
                elif event.key == pygame.K_RETURN:
                    return selected  # 0: manual, 1: automático

def run_manual_game(screen, board, font, rows, cols):
    running = True
    dragging = False
    current_number = None
    row, col = None, None
    row1, col1 = None, None

    while running:
        draw_board(screen, board, font)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                row, col = get_cell_from_mouse(event.pos)
                row1, col1 = row, col
                if 0 <= row < rows and 0 <= col < cols:
                    value = board.grid[row][col]
                    if value is not None:
                        current_number = value
                        board.paths[current_number] = [(row, col)]
                        dragging = True

            elif event.type == pygame.MOUSEMOTION and dragging:
                row, col = get_cell_from_mouse(event.pos)
                if row != row1 or col != col1:
                    if board.is_valid_move(row, col, row1, col1, current_number):
                        if (row, col) != board.paths[current_number][-1]:
                            value = board.grid[row][col]

                            if value == current_number and (row, col) != board.paths[current_number][0]:
                                board.add_to_path(current_number, (row, col))
                                dragging = False
                                current_number = None
                                if is_game_completed(board):
                                    font_big = pygame.font.SysFont("Arial", 36)
                                    text = font_big.render("¡Juego terminado!", True, (0, 128, 0))
                                    text_rect = text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
                                    screen.blit(text, text_rect)
                                    pygame.display.flip()
                                    pygame.time.delay(2000)
                                    running = False
                                continue

                            if value is None:
                                row1, col1 = row, col
                                board.add_to_path(current_number, (row, col))

            elif event.type == pygame.MOUSEBUTTONUP:
                dragging = False
                current_number = None

    pygame.quit()

def run_solver(screen, board, font):
    # Placeholder: Aquí se colocará el algoritmo automático
    print("Modo automático aún no implementado.")
    pygame.quit()

def main():
    pygame.init()

    rows, cols, pairs = read_board_file("example.txt")
    board = Board(rows, cols, pairs)

    width = MARGIN * 2 + cols * CELL_SIZE
    height = MARGIN * 2 + rows * CELL_SIZE
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("NumberLink")

    font = pygame.font.SysFont("Arial", FONT_SIZE)

    # Mostrar menú y seleccionar modo
    choice = show_menu(screen, font)

    if choice == 1:
        run_solver(screen, board, font)
    else:
        run_manual_game(screen, board, font, rows, cols)

if __name__ == "__main__":
    main()
