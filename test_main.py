# test_main.py

import unittest
import pygame  # Solo para inicializar fonts si fuera necesario
import sys

# Importamos las funciones y clases que vamos a probar
from main import get_cell_from_mouse, has_dead_end, a_star_all_paths
from board import Board

# Importamos constantes de UI para get_cell_from_mouse
from ui import MARGIN, CELL_SIZE


class TestMainFunctions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Algunas funciones no necesitan Pygame, pero dejamos esto por si en el futuro fuese necesario.
        pygame.init()

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def test_get_cell_from_mouse(self):
        """
        Probamos get_cell_from_mouse() con varias posiciones:
          - Caso 1: clic justo en el borde superior izquierdo de la celda (fila=0, col=0)
          - Caso 2: clic en el centro de la celda (fila=2, col=3)
          - Caso 3: clic fuera de cualquier celda (negativo o muy grande), 
                    la función seguirá devolviendo índices incluso si están fuera de rango de tablero
        """
        # Caso 1: fila=0, col=0
        x1 = MARGIN + 0 * CELL_SIZE + 0
        y1 = MARGIN + 0 * CELL_SIZE + 0
        output1 = get_cell_from_mouse((x1, y1))
        print(f"get_cell_from_mouseEntrada: pos=({x1},{y1}) → Salida: {output1}")
        self.assertEqual(output1, (0, 0))

        # Caso 2: fila=2, col=3 (tomamos el punto superior izquierdo de esa celda)
        x2 = MARGIN + 3 * CELL_SIZE
        y2 = MARGIN + 2 * CELL_SIZE
        output2 = get_cell_from_mouse((x2, y2))
        print(f"get_cell_from_mouse Entrada: pos=({x2},{y2}) → Salida: {output2}")
        self.assertEqual(output2, (2, 3))

        # Caso 3: clic fuera del margen (negativo)
        x3 = -10
        y3 = -5
        output3 = get_cell_from_mouse((x3, y3))
        print(f"get_cell_from_mouse Entrada: pos=({x3},{y3}) → Salida: {output3}")
        # Aun así devuelve índices, aquí (-1, -1) dado cómo se calcula
        self.assertEqual(output3, ((-5 - MARGIN) // CELL_SIZE, (-10 - MARGIN) // CELL_SIZE))

    def test_has_dead_end_empty_board(self):
        """
        Creamos un tablero 2x2 sin pares. Ninguna celda está en 'occupied' ni tiene número,
        por lo que cada celda tiene al menos un vecino vacío → no hay callejones sin salida.
        """
        rows, cols = 2, 2
        pairs = {}  # Sin pares, todas las celdas en None
        board = Board(rows, cols, pairs)
        occupied = set()
        output = has_dead_end(board, occupied)
        print(f"has_dead_end Entrada: tablero 2x2 vacío, occupied={occupied} → Salida: {output}")
        self.assertFalse(output)

    def test_has_dead_end_single_isolated_cell(self):
        """
        Tablero 1x1 sin pares. La única celda no está en 'occupied' y no tiene vecinos,
        por lo que es un callejón sin salida (la función debe devolver True).
        """
        rows, cols = 1, 1
        pairs = {}
        board = Board(rows, cols, pairs)
        occupied = set()
        output = has_dead_end(board, occupied)
        print(f"has_dead_end Entrada: tablero 1x1 vacío, occupied={occupied} → Salida: {output}")
        self.assertTrue(output)

    def test_has_dead_end_with_blocked_neighbors(self):
        """
        Tablero 3x3, definimos un par en (0,0) y (2,2) de modo que no se utilizan estas celdas
        de prueba. Marcamos manualmente 'occupied' en todas las celdas excepto (1,1). 
        Entonces (1,1) no tiene vecinos libres → dead end = True.
        """
        rows, cols = 3, 3
        # Definimos un par que no tocamos en el test; su presencia solo crea un grid con números
        pairs = {1: [(0, 0), (2, 2)]}
        board = Board(rows, cols, pairs)
        # Marcamos como ocupadas todas las celdas excepto (1,1)
        occupied = {(r, c) for r in range(rows) for c in range(cols) if not (r == 1 and c == 1)}
        output = has_dead_end(board, occupied)
        print(f"has_dead_end Entrada: tablero 3x3, occupied={occupied} → Salida: {output}")
        self.assertTrue(output)

    def test_a_star_all_paths_simple(self):
        """
        Tablero 2x2 sin pares. Probamos caminos de (0,0) a (1,1).
        Hay dos rutas más cortas posibles:
            1) (0,0) → (0,1) → (1,1)
            2) (0,0) → (1,0) → (1,1)
        a_star_all_paths debe devolver ambas (en cualquier orden), 
        y no usar celdas 'occupied'.
        """
        rows, cols = 2, 2
        pairs = {}  # Sin pares, todas las celdas None
        board = Board(rows, cols, pairs)
        occupied = set()  # Ninguna celda bloqueada

        start = (0, 0)
        goal = (1, 1)
        paths = a_star_all_paths(start, goal, occupied, board, max_paths=10)

        print(f"a_star_all_paths Entrada: start={start}, goal={goal}, occupied={occupied} → Salida: {paths}")

        # Convertimos a sets de tuplas para comparar sin importar el orden
        expected_path_1 = [(0, 0), (0, 1), (1, 1)]
        expected_path_2 = [(0, 0), (1, 0), (1, 1)]

        # Debe encontrar al menos estas dos rutas (puede recorrerlas en distinto orden)
        self.assertTrue(any(path == expected_path_1 for path in paths))
        self.assertTrue(any(path == expected_path_2 for path in paths))
        # Ningún camino debe pasar por celdas ocupadas
        for path in paths:
            for cell in path:
                self.assertNotIn(cell, occupied)

    def test_a_star_all_paths_with_obstacle(self):
        """
        Tablero 3x3 sin pares. Bloqueamos la celda central (1,1). 
        Pedimos caminos de (0,0) a (2,2). A* debe evitar (1,1).
        Rutas válidas:
            1) (0,0)->(0,1)->(0,2)->(1,2)->(2,2)
            2) (0,0)->(1,0)->(2,0)->(2,1)->(2,2)
            3) otras combinaciones que no pasen por (1,1).
        """
        rows, cols = 3, 3
        pairs = {}
        board = Board(rows, cols, pairs)
        occupied = {(1, 1)}  # Bloqueamos el centro

        start = (0, 0)
        goal = (2, 2)
        paths = a_star_all_paths(start, goal, occupied, board, max_paths=10)

        print(f"a_star_all_paths (obstáculo) Entrada: start={start}, goal={goal}, occupied={occupied} → Salida: {paths}")

        # Verificamos que ninguna ruta pase por (1,1)
        for path in paths:
            self.assertNotIn((1, 1), path)

        # Al menos hay una ruta válida (la que da la vuelta al obstáculo)
        self.assertTrue(len(paths) >= 1)

    # NOTA: Las otras funciones de main.py dependen de Pygame en tiempo real
    # (show_menu, run_manual_game, run_solver2, main), por lo que no las probamos aquí
    # con pruebas unitarias estrictas. Dejaríamos su testeo para un entorno de integración.
    # Si en tu documentación necesitas mencionar que están "no testeadas" en esta suite,
    # bastaría con anotarlo en la sección de cobertura.


if __name__ == "__main__":
    print("\n--- Ejecutando pruebas unitarias de main.py ---\n")
    unittest.main(verbosity=2)
