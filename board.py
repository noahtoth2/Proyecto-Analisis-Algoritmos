# board.py

class Board:
    def __init__(self, rows, cols, pairs):
        self.rows = rows
        self.cols = cols
        self.pairs = pairs  # {number: [(r1, c1), (r2, c2)]}
        self.grid = [[None for _ in range(cols)] for _ in range(rows)]
        self.paths = {}  # {number: [(r, c), (r, c), ...]}

        for number, positions in pairs.items():
            for r, c in positions:
                self.grid[r][c] = number

    def is_valid_move(self, r, c, current_number):
        if not (0 <= r < self.rows and 0 <= c < self.cols):
            return False
        if self.grid[r][c] is not None and self.grid[r][c] != current_number:
            return False
        for path in self.paths.values():
            if (r, c) in path:
                return False
        return True

    def add_to_path(self, number, position):
        if number not in self.paths:
            self.paths[number] = []
        self.paths[number].append(position)

    def remove_last_from_path(self, number):
        if number in self.paths and self.paths[number]:
            self.paths[number].pop()