# main.py

import pygame
import sys
import time
from collections import deque
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
                sys.exit()
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

    start_time = time.time()
    clock = pygame.time.Clock()  # Para controlar FPS

    while running:
        elapsed_time = int(time.time() - start_time)
        draw_board(screen, board, font)

        # Mostrar temporizador
        minutes = elapsed_time // 60
        seconds = elapsed_time % 60
        timer_text = font.render(f"Tiempo: {minutes:02d}:{seconds:02d}", True, (0, 0, 255))
        screen.blit(timer_text, (10, 10))

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

        clock.tick(30)  # Limita a 30 FPS para evitar uso excesivo de CPU

    pygame.quit()

def run_solver(screen, board, font):
    rows, cols = board.rows, board.cols

    pairs_list = []
    for number, positions in board.pairs.items():
        (r1, c1), (r2, c2) = positions
        dist = abs(r1 - r2) + abs(c1 - c2)
        pairs_list.append((number, (r1, c1), (r2, c2), dist))
    pairs_list.sort(key=lambda x: x[3])

    def bfs_path(start, goal, occupied):
        q = deque([start])
        prev = {start: None}
        visited = {start}

        while q:
            cur = q.popleft()
            if cur == goal:
                path = []
                node = goal
                while node is not None:
                    path.append(node)
                    node = prev[node]
                path.reverse()
                return path

            r, c = cur
            for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
                nr, nc = r + dr, c + dc
                neigh = (nr, nc)
                if not (0 <= nr < rows and 0 <= nc < cols):
                    continue
                if neigh in occupied and neigh != goal:
                    continue
                if neigh not in visited:
                    visited.add(neigh)
                    prev[neigh] = cur
                    q.append(neigh)
        return None

    occupied = set()
    for number, positions in board.pairs.items():
        for pos in positions:
            occupied.add(pos)

    board.paths.clear()
    heuristic_success = True

    for number, start, goal, _ in pairs_list:
        path = bfs_path(start, goal, occupied)
        if path is None:
            heuristic_success = False
            break
        board.paths[number] = path
        for cell in path:
            occupied.add(cell)

    if heuristic_success and is_game_completed(board):
        draw_board(screen, board, font)
        msg = "¡Tablero resuelto (heurística)!"
        color = (0, 128, 0)
        text = font.render(msg, True, color)
        screen.blit(text, (screen.get_width() // 2 - text.get_width() // 2, 20))
        pygame.display.flip()
        pygame.time.delay(3000)
        pygame.quit()
        return

    screen.fill((255, 255, 255))
    msg = "Buscando solución con backtracking..."
    text = font.render(msg, True, (0, 0, 0))
    screen.blit(text, (screen.get_width() // 2 - text.get_width() // 2, 20))
    pygame.display.flip()

    occupied = set()
    for number, positions in board.pairs.items():
        for pos in positions:
            occupied.add(pos)
    board.paths.clear()

    pairs_order = [(num, start, goal) for (num, start, goal, _) in pairs_list]

    start_time = time.time()
    TIME_LIMIT = 100  # segundos

    def solve_pairs(idx):
        if time.time() - start_time > TIME_LIMIT:
            return False

        if idx >= len(pairs_order):
            return True

        number, start, goal = pairs_order[idx]
        path_partial = [start]
        occupied.add(start)

        def extend_path(cell):
            if time.time() - start_time > TIME_LIMIT:
                return False

            if cell == goal:
                board.paths[number] = path_partial.copy()
                if solve_pairs(idx + 1):
                    return True
                board.paths.pop(number, None)
                return False

            r, c = cell
            gr, gc = goal
            vecinos = []
            for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
                nr, nc = r + dr, c + dc
                if not (0 <= nr < rows and 0 <= nc < cols):
                    continue
                neigh = (nr, nc)
                if neigh in occupied and neigh != goal:
                    continue
                dist_manh = abs(nr - gr) + abs(nc - gc)
                vecinos.append((dist_manh, neigh))
            vecinos.sort(key=lambda x: x[0])

            for _, neigh in vecinos:
                if neigh in occupied and neigh != goal:
                    continue
                path_partial.append(neigh)
                occupied.add(neigh)

                draw_board(screen, board, font)
                pygame.display.flip()
                pygame.time.delay(20)

                if extend_path(neigh):
                    return True

                path_partial.pop()
                occupied.discard(neigh)

            return False

        if extend_path(start):
            return True
        occupied.remove(start)
        return False

    success = solve_pairs(0)

    draw_board(screen, board, font)
    if success and is_game_completed(board):
        msg = "¡Tablero resuelto (backtracking)!"
        color = (0, 128, 0)
    else:
        msg = "No se encontró solución (ni heurística ni backtracking)."
        color = (255, 0, 0)

    text = font.render(msg, True, color)
    screen.blit(text, (screen.get_width() // 2 - text.get_width() // 2, 20))
    pygame.display.flip()
    pygame.time.delay(3000)
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

    choice = show_menu(screen, font)

    if choice == 1:
        run_solver(screen, board, font)
    else:
        run_manual_game(screen, board, font, rows, cols)

if __name__ == "__main__":
    main()
