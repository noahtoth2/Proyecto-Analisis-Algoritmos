# board_parser.py

def read_board_file(filename):
    with open(filename, "r") as file:
        lines = file.readlines()

    # Obtener tamaño del tablero
    n_rows, n_cols = map(int, lines[0].strip().split(','))

    # Leer las coordenadas de los números
    pairs = {}
    for line in lines[1:]:
        row, col, number = map(int, line.strip().split(','))
        if number not in pairs:
            pairs[number] = []
        pairs[number].append((row - 1, col - 1))  # Convertimos a índice base 0

    return n_rows, n_cols, pairs