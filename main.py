# main.py

import pygame
from board_parser import read_board_file
from board import Board
from ui import draw_board, CELL_SIZE, MARGIN, FONT_SIZE

def get_cell_from_mouse(pos):
    x, y = pos
    col = (x - MARGIN) // CELL_SIZE
    row = (y - MARGIN) // CELL_SIZE
    return row, col

def main():
    pygame.init()

    rows, cols, pairs = read_board_file("example.txt")
    board = Board(rows, cols, pairs)

    width = MARGIN * 2 + cols * CELL_SIZE
    height = MARGIN * 2 + rows * CELL_SIZE
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("NumberLink - Interfaz Humano")

    font = pygame.font.SysFont("Arial", FONT_SIZE)

    running = True
    dragging = False
    current_number = None
    row , col = None, None
    row1, col1 = None, None

    while running:
        draw_board(screen, board, font)
        pygame.display.flip()

        for event in pygame.event.get():


            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                row, col = get_cell_from_mouse(event.pos)
                row1,col1 = row,col
                print(row, col, row1, col1)
                if 0 <= row < rows and 0 <= col < cols:
                    value = board.grid[row][col]
                    if value is not None:
                        current_number = value
                        board.paths[current_number] = [(row, col)]
                        dragging = True

            elif event.type == pygame.MOUSEMOTION and dragging:
                row, col = get_cell_from_mouse(event.pos)
                if row != row1 or col != col1:
                    if board.is_valid_move(row, col,row1, col1, current_number):
                        if (row, col) != board.paths[current_number][-1]:
                            row1, col1 = row, col
                            print(row, col, row1, col1)
                            board.add_to_path(current_number, (row, col))

            elif event.type == pygame.MOUSEBUTTONUP:
                dragging = False
                current_number = None

    pygame.quit()

if __name__ == "__main__":
    main()
