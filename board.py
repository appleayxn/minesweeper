"""
Minesweeper - Algorithms and Programming 1 - UFAZ
Team: Zeynalzada Ayxan, Maharramli Anvar, Qurbanli Elton,
      Nuruzada Nihat, Hamzayev Altair
File: board.py
Role: constants, board creation, mine placement, neighbours and numbers
"""

import random

# ---------- Constants (written in CAPITALS, never changed) ----------

HIDDEN = "#"        # a cell that is not revealed yet
FLAG = "F"          # a cell where the player put a flag
EMPTY = "."         # a revealed cell with 0 mines around it
MINE = "*"          # a mine (shown at the end or in debug mode)
HIT = "X"           # the mine the player revealed
WRONG_FLAG = "!"    # a flag on a cell without a mine (end of game)

# the names of the columns shown on the screen
LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

# level number -> (number of rows, number of columns, number of mines)
LEVELS = {1: (9, 9, 10), 2: (12, 12, 25), 3: (16, 16, 40)}

# level number -> name of the level
LEVEL_NAMES = {1: "Easy", 2: "Medium", 3: "Hard"}


def create_board(rows, cols):
    """Create the board that the player sees. All cells are hidden.

    Parameters:
        rows (int): number of rows
        cols (int): number of columns

    Returns:
        list: a list of lists, every cell contains HIDDEN
    """
    board = []
    for r in range(rows):
        line = []                     # a new empty row
        for c in range(cols):
            line.append(HIDDEN)       # add one hidden cell to the row
        board.append(line)            # add the row to the board
    return board


def neighbours(row, col, rows, cols):
    """Find all the cells around one cell (at most 8 cells).

    This is the only function that looks for neighbours.
    All the other functions use it.

    Parameters:
        row (int): row of the cell (starts at 0)
        col (int): column of the cell (starts at 0)
        rows (int): number of rows of the board
        cols (int): number of columns of the board

    Returns:
        list: list of tuples (r, c), the neighbours inside the board
    """
    result = []
    for dr in [-1, 0, 1]:             # row above, same row, row below
        for dc in [-1, 0, 1]:         # column left, same column, column right
            r = row + dr
            c = col + dc

            # (dr, dc) = (0, 0) is the cell itself, it is not a neighbour
            is_the_cell_itself = False
            if dr == 0 and dc == 0:
                is_the_cell_itself = True

            # the neighbour must be inside the board
            is_inside = False
            if r >= 0 and r < rows and c >= 0 and c < cols:
                is_inside = True

            if is_inside and not is_the_cell_itself:
                result.append((r, c))
    return result


def place_mines(rows, cols, nb_mines, safe_cell):
    """Choose the positions of the mines at random, never on safe_cell.

    The list of possible cells is always built in the same order
    (row by row), so the same seed always gives the same mines.

    Parameters:
        rows (int): number of rows
        cols (int): number of columns
        nb_mines (int): how many mines to place
        safe_cell (tuple): (row, col) of the first cell the player revealed

    Returns:
        set: set of tuples (r, c), the positions of the mines
    """
    # 1. make a list of all the cells, except the safe cell
    candidates = []
    for r in range(rows):
        for c in range(cols):
            if (r, c) != safe_cell:
                candidates.append((r, c))

    # 2. random.sample chooses nb_mines different cells from the list
    chosen = random.sample(candidates, nb_mines)

    # 3. put the chosen cells in a set
    mines = set()
    for cell in chosen:
        mines.add(cell)
    return mines


def place_mines_safe(rows, cols, nb_mines, safe_cell):
    """OPTIONAL EXTRA - like place_mines, but the 8 neighbours of
    safe_cell are also free of mines (safer first move).

    So the first revealed cell always shows 0 and opens an area.

    Parameters:
        rows (int): number of rows
        cols (int): number of columns
        nb_mines (int): how many mines to place
        safe_cell (tuple): (row, col) of the first cell the player revealed

    Returns:
        set: set of tuples (r, c), the positions of the mines
    """
    # 1. the cells where no mine can go: the safe cell and its neighbours
    forbidden = neighbours(safe_cell[0], safe_cell[1], rows, cols)
    forbidden.append(safe_cell)

    # 2. make a list of all the other cells
    candidates = []
    for r in range(rows):
        for c in range(cols):
            if (r, c) not in forbidden:
                candidates.append((r, c))

    # 3. random.sample chooses nb_mines different cells from the list
    chosen = random.sample(candidates, nb_mines)

    # 4. put the chosen cells in a set
    mines = set()
    for cell in chosen:
        mines.add(cell)
    return mines


def count_adjacent(row, col, mines, rows, cols):
    """Count how many mines are around one cell.

    Parameters:
        row (int): row of the cell
        col (int): column of the cell
        mines (set): set of tuples (r, c) of the mines
        rows (int): number of rows
        cols (int): number of columns

    Returns:
        int: the number of mines around the cell (0 to 8)
    """
    count = 0
    around = neighbours(row, col, rows, cols)
    for cell in around:
        if cell in mines:
            count = count + 1
    return count


def compute_numbers(mines, rows, cols):
    """Compute, for every cell, how many mines are around it.

    Parameters:
        mines (set): set of tuples (r, c) of the mines
        rows (int): number of rows
        cols (int): number of columns

    Returns:
        list: a list of lists of int, numbers[r][c] for every cell
    """
    numbers = []
    for r in range(rows):
        line = []
        for c in range(cols):
            how_many = count_adjacent(r, c, mines, rows, cols)
            line.append(how_many)
        numbers.append(line)
    return numbers
