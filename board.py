"""
Minesweeper - Algorithms and Programming 1 - UFAZ
Team: Zeynalzada Ayxan, Maharramli Anvar, Qurbanli Elton,
      Nuruzada Nihat, Hamzayev Altair
File: board.py
Role: constants, board creation, mine placement, neighbours and numbers
"""

import random

# ---------- Constants (written in CAPITALS, never modified) ----------
HIDDEN = '#'        # cell not revealed yet
FLAG = 'F'          # cell marked by the player as a possible mine
EMPTY = '.'         # revealed cell with 0 neighbouring mines
MINE = '*'          # mine shown at the end or in debug mode
HIT = 'X'           # the mine the player revealed
WRONG_FLAG = '!'    # flag placed on a cell that is not a mine (end of game)

LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"   # column names shown on screen

# level number -> (rows, columns, number of mines)
LEVELS = {1: (9, 9, 10), 2: (12, 12, 25), 3: (16, 16, 40)}
LEVEL_NAMES = {1: "Easy", 2: "Medium", 3: "Hard"}


def create_board(rows, cols):
    """Create the board the player sees, with every cell hidden.

    Parameters:
        rows (int): number of rows
        cols (int): number of columns

    Returns:
        list: list of lists of str, every cell equal to HIDDEN
    """
    board = []
    for r in range(rows):
        board.append([HIDDEN] * cols)   # a new list for each row
    return board


def neighbours(row, col, rows, cols):
    """Return the valid neighbours of a cell (up to 8).

    This is the only function that computes neighbours; every other
    function uses it.

    Parameters:
        row (int): row index, starting at 0
        col (int): column index, starting at 0
        rows (int): number of rows of the board
        cols (int): number of columns of the board

    Returns:
        list: tuples (r, c) of the cells around (row, col) inside the board
    """
    result = []
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr == 0 and dc == 0:
                continue                      # the cell itself is skipped
            r = row + dr
            c = col + dc
            if 0 <= r < rows and 0 <= c < cols:   # keep cells inside the board
                result.append((r, c))
    return result


def place_mines(rows, cols, nb_mines, safe_cell):
    """Choose the mine positions at random, never on the safe cell.

    The candidates are built in a fixed row-by-row order (a list, not a
    set), so the same seed always gives the same mines.

    Parameters:
        rows (int): number of rows
        cols (int): number of columns
        nb_mines (int): number of mines to place
        safe_cell (tuple): (row, col) of the first revealed cell

    Returns:
        set: tuples (r, c) of the mines
    """
    candidates = []
    for r in range(rows):
        for c in range(cols):
            if (r, c) != safe_cell:
                candidates.append((r, c))
    chosen = random.sample(candidates, nb_mines)   # nb_mines different cells
    return set(chosen)


def count_adjacent(row, col, mines, rows, cols):
    """Count the mines around one cell.

    Parameters:
        row (int): row index
        col (int): column index
        mines (set): tuples (r, c) of the mines
        rows (int): number of rows
        cols (int): number of columns

    Returns:
        int: number of mines among the neighbours (0 to 8)
    """
    count = 0
    for cell in neighbours(row, col, rows, cols):
        if cell in mines:          # O(1) on average because mines is a set
            count += 1
    return count


def compute_numbers(mines, rows, cols):
    """Compute, for every cell, how many neighbouring cells are mines.

    Parameters:
        mines (set): tuples (r, c) of the mines
        rows (int): number of rows
        cols (int): number of columns

    Returns:
        list: list of lists of int, numbers[r][c] for every cell
    """
    numbers = []
    for r in range(rows):
        line = []
        for c in range(cols):
            line.append(count_adjacent(r, c, mines, rows, cols))
        numbers.append(line)
    return numbers
