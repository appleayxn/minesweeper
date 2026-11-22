"""
Minesweeper - Algorithms and Programming 1 - UFAZ
Team: Zeynalzada Ayxan, Maharramli Anvar, Qurbanli Elton,
      Nuruzada Nihat, Hamzayev Altair
File: interface.py
Role: level and seed choice, display, command parsing, help
"""

import random

from board import (HIDDEN, FLAG, EMPTY, MINE, HIT, WRONG_FLAG,
                   LETTERS, LEVELS, LEVEL_NAMES)

DIGITS = "0123456789"


def is_number(text):
    """Check that a string contains only the digits 0-9.

    str.isdigit() is not used because it also accepts characters like
    the superscript two that int() cannot convert, which would crash the program.

    Parameters:
        text (str): the text to check

    Returns:
        bool: True if text is not empty and made only of 0-9
    """
    if text == "":
        return False
    for ch in text:
        if ch not in DIGITS:
            return False
    return True


def choose_level():
    """Ask the player for the level and an optional seed.

    The questions are repeated until the answers are valid.

    If the player gives no seed, a random seed is chosen and shown, so
    that every game can be replayed exactly.

    Returns:
        tuple: (rows, cols, nb_mines, seed)
    """
    print()
    for number in LEVELS:
        rows, cols, mines = LEVELS[number]
        print("  " + str(number) + " - " + LEVEL_NAMES[number] + ": "
              + str(rows) + " x " + str(cols) + ", " + str(mines) + " mines")
    level = 0
    while level == 0:
        answer = input("Choose a level (1, 2 or 3): ").strip()
        if answer in ("1", "2", "3"):
            level = int(answer)
        else:
            print("Please choose 1, 2 or 3.")

    seed = None
    asking = True
    while asking:
        answer = input("Seed (a number, or press Enter for random): ").strip()
        if answer == "":
            seed = random.randint(1, 999999)   # random game, but replayable
            asking = False
        elif is_number(answer):
            seed = int(answer)
            asking = False
        else:
            print("The seed must be a whole number (digits only).")

    rows, cols, nb_mines = LEVELS[level]
    print(LEVEL_NAMES[level] + " level, seed " + str(seed))
    return rows, cols, nb_mines, seed


def cell_symbol(cell, state, show_mines):
    """Return the symbol to print for one cell.

    Parameters:
        cell (tuple): (row, col)
        state (dict): the game state
        show_mines (bool): True to show the mines (debug or end of game)

    Returns:
        str: one character
    """
    if show_mines:
        if cell == state["hit_mine"]:
            return HIT
        if cell in state["flags"] and cell not in state["mines"]:
            if state["game_over"]:
                return WRONG_FLAG          # wrong flags only at the end
            return FLAG
        if cell in state["mines"] and cell not in state["flags"]:
            return MINE
    return state["board"][cell[0]][cell[1]]


def display_board(state, show_mines):
    """Print the board with column letters, row numbers and mines left.

    Parameters:
        state (dict): the game state
        show_mines (bool): True to show the mines (debug or end of game)

    Returns:
        None
    """
    rows = state["rows"]
    cols = state["cols"]
    print()
    header = "   "
    for c in range(cols):
        header += LETTERS[c] + " "
    print(header)
    for r in range(rows):
        line = str(r + 1).rjust(2) + " "    # rows 1-9 aligned with 10-16
        for c in range(cols):
            line += cell_symbol((r, c), state, show_mines) + " "
        print(line)
    mines_left = state["nb_mines"] - len(state["flags"])
    print("Mines left: " + str(mines_left))


def parse_cell(text, rows, cols):
    """Convert a cell written like 'C4' into (row, col).

    Parameters:
        text (str): the cell, already in upper case, e.g. 'C4'
        rows (int): number of rows
        cols (int): number of columns

    Returns:
        tuple: ((row, col), "") if valid, or (None, error message)
    """
    if len(text) < 2 or text[0] not in LETTERS or not is_number(text[1:]):
        return None, "Invalid cell. Write a letter then a number, e.g. E5."
    col = ord(text[0]) - ord('A')     # 'A' -> 0, 'B' -> 1, ...
    row = int(text[1:]) - 1           # rows start at 1 on screen, 0 inside
    if row < 0 or row >= rows or col >= cols:
        return None, "Cell outside the board."
    return (row, col), ""


def parse_command(text, rows, cols):
    """Read one line typed by the player and check it.

    Accepted commands (not case-sensitive): R <cell>, F <cell>, D, H, Q.
    This function never raises an exception, whatever the input.

    Parameters:
        text (str): the line typed by the player
        rows (int): number of rows
        cols (int): number of columns

    Returns:
        tuple: (command, cell) if valid - cell is (row, col) or None;
               (None, error message) otherwise
    """
    parts = text.strip().upper().split()
    if len(parts) == 0:
        return None, "Please type a command (H for help)."
    command = parts[0]
    if command not in ("R", "F", "D", "H", "Q"):
        return None, "Unknown command '" + parts[0] + "'. Type H for help."
    if command in ("D", "H", "Q"):
        if len(parts) > 1:
            return None, "Command " + command + " does not take a cell."
        return command, None
    if len(parts) == 1:
        return None, "Missing cell, e.g. " + command + " E5."
    if len(parts) > 2:
        return None, "Too many words, e.g. " + command + " E5."
    cell, error = parse_cell(parts[1], rows, cols)
    if cell is None:
        return None, error
    return command, cell


def show_help():
    """Print the list of commands and symbols.

    Returns:
        None
    """
    print()
    print("Commands (upper or lower case):")
    print("  R E5   reveal cell E5")
    print("  F C3   put or remove a flag on C3")
    print("  D      debug: show all mines (the game continues)")
    print("  H      show this help")
    print("  Q      quit the current game")
    print("Symbols:")
    print("  " + HIDDEN + " hidden   " + FLAG + " flag   " + EMPTY
          + " empty   1-8 mines around")
    print("  " + MINE + " mine   " + HIT + " mine you hit   "
          + WRONG_FLAG + " wrong flag (end of game)")
