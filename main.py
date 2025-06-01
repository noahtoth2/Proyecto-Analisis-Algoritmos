# main.py

import pygame
import sys
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
    """
    Función idéntica a tu modo manual. No cambió nada de lógica,
    sólo se movió al interior de una función para integrarlo con el menú.
    """
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

                            # Si llegamos al segundo número (pero no al mismo del inicio)
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

                            # Si es una celda vacía, continuar trazo
                            if value is None:
                                row1, col1 = row, col
                                board.add_to_path(current_number, (row, col))

            elif event.type == pygame.MOUSEBUTTONUP:
                dragging = False
                current_number = None

    pygame.quit()

def run_solver(screen, board, font):
    """
    MODIFICACIÓN: aquí incorporamos dos estrategias en cascada:
      1) Heurística BFS ordenada por distancia.
      2) Si falla, backtracking completo con poda basada en distancia.
    """

    rows, cols = board.rows, board.cols

    # ------------------------------------------------------------
    # Paso 1: Construir lista de pares ordenados por distancia Manhattan
    # ------------------------------------------------------------
    pairs_list = []
    for number, positions in board.pairs.items():
        (r1, c1), (r2, c2) = positions
        dist = abs(r1 - r2) + abs(c1 - c2)
        pairs_list.append((number, (r1, c1), (r2, c2), dist))
    pairs_list.sort(key=lambda x: x[3])  # ascendente por distancia
    # Ahora pairs_list = [(num, start, goal, manhattan), ...]

    # ------------------------------------------------------------
    # Paso 2: Intentar la HEURÍSTICA BFS rápida
    # ------------------------------------------------------------
    def bfs_path(start, goal, occupied):
        """
        Devuelve la ruta más corta (lista de celdas) de start a goal usando BFS,
        bloqueando todas las celdas en 'occupied' salvo el propio goal.
        """
        q = deque([start])
        prev = {start: None}
        visited = {start}

        while q:
            cur = q.popleft()
            if cur == goal:
                # Reconstruir camino
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
                # Limites
                if not (0 <= nr < rows and 0 <= nc < cols):
                    continue
                # Si está ocupado y no es el goal, lo saltamos
                if neigh in occupied and neigh != goal:
                    continue
                if neigh not in visited:
                    visited.add(neigh)
                    prev[neigh] = cur
                    q.append(neigh)
        return None

    # Inicialmente, asumimos que todos los números fijos están ocupados
    occupied = set()
    for number, positions in board.pairs.items():
        for pos in positions:
            occupied.add(pos)

    # Intentamos asignar rutas con BFS en orden de distancia
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

    # Si la heurística completó con éxito y el tablero está lleno, mostramos el resultado
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

    # ------------------------------------------------------------
    # Paso 3: Si la heurística falló, reiniciamos y aplicamos BACKTRACKING
    # ------------------------------------------------------------
    # Preparamos 'occupied' de nuevo sólo con celdas de números fijos
    occupied = set()
    for number, positions in board.pairs.items():
        for pos in positions:
            occupied.add(pos)
    board.paths.clear()

    # Extraemos sólo (number, start, goal) del pairs_list
    pairs_order = [(num, start, goal) for (num, start, goal, _) in pairs_list]

    # Función recursiva: tratar de resolver pares desde el índice `idx`
    def solve_pairs(idx):
        """
        - idx: índice en pairs_order que estamos intentando conectar.
        - Si idx == len(pairs_order), devolvemos True (todos conectados).
        - Sino, intentamos backtracking para el par en pairs_order[idx].
        """
        if idx >= len(pairs_order):
            # Todos los pares conectados
            return True

        number, start, goal = pairs_order[idx]

        # Función DFS para extender paso a paso la ruta del par actual
        path_partial = [start]  # comenzamos en la celda de inicio
        occupied.add(start)

        def extend_path(cell):
            """
            - cell: celda actual en la ruta parcial.
            - Si llegamos a goal, guardamos ruta y llamamos a solve_pairs(idx+1).
            - Si solve_pairs(idx+1) es True, retornamos True.
            - Si no, retrocedemos (backtrack) y probamos otro vecino.
            """
            if cell == goal:
                # Ruta completa para este par
                board.paths[number] = path_partial.copy()
                # Proceder a resolver el siguiente par
                if solve_pairs(idx + 1):
                    return True
                # Si no tuvo éxito, borramos esta ruta antes de seguir probando
                board.paths.pop(number, None)
                return False

            r, c = cell
            # Vecinos ortogonales ordenados por cercanía al goal (heurística local)
            vecinos = []
            gr, gc = goal
            for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
                nr, nc = r + dr, c + dc
                if not (0 <= nr < rows and 0 <= nc < cols):
                    continue
                neigh = (nr, nc)
                # Sólo podemos moverte a neigh si:
                # 1) No está en occupied, o bien 2) es el goal
                if neigh in occupied and neigh != goal:
                    continue
                # En ese caso, consideramos movernos ahí
                dist_manh = abs(nr - gr) + abs(nc - gc)
                vecinos.append((dist_manh, neigh))
            # Ordenamos vecinos por distancia creciente al goal
            vecinos.sort(key=lambda x: x[0])

            for _, neigh in vecinos:
                # Si neigh ya está en occupied y no es goal, no lo usamos
                if neigh in occupied and neigh != goal:
                    continue
                # Marcamos tente ocupado y seguimos
                path_partial.append(neigh)
                occupied.add(neigh)

                if extend_path(neigh):
                    return True

                # Backtrack: sacamos neigh de path_partial y occupied
                path_partial.pop()
                occupied.discard(neigh)

            return False  # Ninguna opción de vecino funcionó

        # Llamada inicial desde la celda start
        if extend_path(start):
            return True
        # Si aquí no devolvió True, significa que NO hay ninguna ruta posible
        # que conecte este par sin bloquear la resolución de los siguientes.
        occupied.remove(start)
        return False

    # Iniciar backtracking desde el par 0
    success = solve_pairs(0)

    # ------------------------------------------------------------
    # Paso 4: Mostrar resultado de backtracking (éxito o fallo total)
    # ------------------------------------------------------------
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

    # Mostrar menú y seleccionar modo
    choice = show_menu(screen, font)

    if choice == 1:
        run_solver(screen, board, font)
    else:
        run_manual_game(screen, board, font, rows, cols)

if __name__ == "__main__":
    main()
