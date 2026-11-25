"""
Minesweeper - Algorithms and Programming 1 - UFAZ
Team: Zeynalzada Ayxan, Maharramli Anvar, Qurbanli Elton,
      Nuruzada Nihat, Hamzayev Altair
File: interface.py
Role: level and seed choice, display, command parsing, help
"""

import random

from board import HIDDEN, FLAG, EMPTY, MINE, HIT, WRONG_FLAG
from board import LETTERS, LEVELS, LEVEL_NAMES

DIGITS = "0123456789"


def is_number(text):
    """Check that a text contains only the digits 0 to 9.

    We do not use text.isdigit() because it also accepts characters
    like the small 2 above a letter, and int() cannot convert them.

    Parameters:
        text (str): the text to check

    Returns:
        bool: True if the text is not empty and has only digits
    """
    if text == "":
        return False
    for character in text:
        if character not in DIGITS:
            return False
    return True


def ask_number(question, low, high):
    """OPTIONAL EXTRA - ask a whole number until it is between low and high.

    Parameters:
        question (str): the text shown to the player
        low (int): the smallest number accepted
        high (int): the biggest number accepted

    Returns:
        int: the number typed by the player
    """
    answer_is_good = False
    number = 0
    while answer_is_good == False:
        answer = input(question)
        answer = answer.strip()
        if is_number(answer):
            number = int(answer)
            if number >= low and number <= high:
                answer_is_good = True
        if answer_is_good == False:
            print("Please type a whole number from " + str(low) + " to "
                  + str(high) + ".")
    return number


def choose_custom():
    """OPTIONAL EXTRA - ask the size and the number of mines of a custom board.

    Rows and columns go from 5 to 20.
    At most 25 % of the cells can be mines (one cell out of four).

    Returns:
        tuple: (rows, cols, nb_mines)
    """
    rows = ask_number("Rows (5 to 20): ", 5, 20)
    cols = ask_number("Columns (5 to 20): ", 5, 20)
    max_mines = int(rows * cols / 4)          # 25 % of the cells
    question = "Mines (1 to " + str(max_mines) + "): "
    nb_mines = ask_number(question, 1, max_mines)
    return rows, cols, nb_mines


def choose_level():
    """Ask the player for the level and for a seed (optional).

    The questions are asked again until the answers are correct.
    If the player gives no seed, a random seed is chosen and shown,
    so the same game can be played again.

    Returns:
        tuple: (rows, cols, nb_mines, seed)
    """
    # ----- show the levels -----
    print()
    for number in LEVELS:
        size = LEVELS[number]
        rows = size[0]
        cols = size[1]
        mines = size[2]
        print("  " + str(number) + " - " + LEVEL_NAMES[number] + ": "
              + str(rows) + " x " + str(cols) + ", " + str(mines) + " mines")
    print("  4 - Custom size (extra)")

    # ----- ask the level -----
    level = 0
    while level == 0:
        answer = input("Choose a level (1, 2, 3 or 4): ")
        answer = answer.strip()
        if answer == "1" or answer == "2" or answer == "3" or answer == "4":
            level = int(answer)
        else:
            print("Please choose 1, 2, 3 or 4.")

    if level == 4:
        custom = choose_custom()
        rows = custom[0]
        cols = custom[1]
        nb_mines = custom[2]

    # ----- ask the seed -----
    seed = 0
    asking = True
    while asking:
        answer = input("Seed (a number, or press Enter for random): ")
        answer = answer.strip()
        if answer == "":
            seed = random.randint(1, 999999)    # random, but we show it
            asking = False
        elif is_number(answer):
            seed = int(answer)
            asking = False
        else:
            print("The seed must be a whole number (digits only).")

    # ----- tell the player what was chosen -----
    if level == 4:
        print("Custom board " + str(rows) + " x " + str(cols) + ", "
              + str(nb_mines) + " mines, seed " + str(seed))
    else:
        size = LEVELS[level]
        rows = size[0]
        cols = size[1]
        nb_mines = size[2]
        print(LEVEL_NAMES[level] + " level, seed " + str(seed))
    return rows, cols, nb_mines, seed


def cell_symbol(cell, state, show_mines):
    """Choose the symbol to print for one cell.

    Parameters:
        cell (tuple): (row, col)
        state (dict): the game state
        show_mines (bool): True to show the mines (debug or end of game)

    Returns:
        str: one character
    """
    r = cell[0]
    c = cell[1]
    if show_mines == True:
        # the mine that the player revealed
        if cell == state["hit_mine"]:
            return HIT
        # a flag on a cell without a mine
        if cell in state["flags"] and cell not in state["mines"]:
            if state["game_over"] == True:
                return WRONG_FLAG      # wrong flags are shown only at the end
            return FLAG
        # a mine without a flag
        if cell in state["mines"] and cell not in state["flags"]:
            return MINE
    # in all the other cases: what the player sees on the board
    return state["board"][r][c]


def display_board(state, show_mines):
    """Print the board with the letters, the row numbers and the mines left.

    Parameters:
        state (dict): the game state
        show_mines (bool): True to show the mines (debug or end of game)

    Returns:
        None
    """
    rows = state["rows"]
    cols = state["cols"]
    print()

    # first line: the letters of the columns
    header = "   "
    for c in range(cols):
        header = header + LETTERS[c] + " "
    print(header)

    # one line for each row of the board
    for r in range(rows):
        row_number = r + 1
        # a space before 1-9 so that they are aligned with 10, 11, ...
        if row_number < 10:
            line = " " + str(row_number) + " "
        else:
            line = str(row_number) + " "
        for c in range(cols):
            line = line + cell_symbol((r, c), state, show_mines) + " "
        print(line)

    mines_left = state["nb_mines"] - len(state["flags"])
    print("Mines left: " + str(mines_left))


def parse_cell(text, rows, cols):
    """Change a cell written like 'C4' into (row, col), here (3, 2).

    Parameters:
        text (str): the cell, already in capital letters, e.g. 'C4'
        rows (int): number of rows
        cols (int): number of columns

    Returns:
        tuple: ((row, col), "") if the cell is correct,
               (None, error message) if it is not
    """
    error = "Invalid cell. Write a letter then a number, e.g. E5."

    # a cell has at least 2 characters: one letter and one digit
    if len(text) < 2:
        return None, error

    letter = text[0]          # first character, e.g. 'C'
    digits = text[1:]         # all the other characters, e.g. '4'

    if letter not in LETTERS:
        return None, error
    if not is_number(digits):
        return None, error

    # find the position of the letter: 'A' -> 0, 'B' -> 1, 'C' -> 2, ...
    col = 0
    for i in range(len(LETTERS)):
        if LETTERS[i] == letter:
            col = i

    # rows start at 1 on the screen but at 0 in the program
    row = int(digits) - 1

    if row < 0 or row >= rows or col >= cols:
        return None, "Cell outside the board."
    return (row, col), ""


def parse_command(text, rows, cols):
    """Read the line typed by the player and check that it is correct.

    Commands (small or capital letters): R <cell>, F <cell>, D, H, Q,
    and the optional extra HINT.
    This function never makes the program crash, whatever the text.

    Parameters:
        text (str): the line typed by the player
        rows (int): number of rows
        cols (int): number of columns

    Returns:
        tuple: (command, cell) if correct (cell is (row, col) or None),
               (None, error message) if not correct
    """
    text = text.strip()        # remove the spaces at the beginning and end
    text = text.upper()        # 'r e5' becomes 'R E5'
    parts = text.split()       # 'R E5' becomes ['R', 'E5']

    if len(parts) == 0:
        return None, "Please type a command (H for help)."

    command = parts[0]

    # commands without a cell
    if command == "D" or command == "H" or command == "Q" or command == "HINT":
        if len(parts) > 1:
            return None, "Command " + command + " does not take a cell."
        return command, None

    # commands with a cell
    if command == "R" or command == "F":
        if len(parts) == 1:
            return None, "Missing cell, e.g. " + command + " E5."
        if len(parts) > 2:
            return None, "Too many words, e.g. " + command + " E5."
        result = parse_cell(parts[1], rows, cols)
        cell = result[0]
        error = result[1]
        if cell == None:
            return None, error
        return command, cell

    # any other word is unknown
    return None, "Unknown command '" + command + "'. Type H for help."


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
    print("  HINT   show a safe cell (extra)")
    print("Symbols:")
    print("  " + HIDDEN + " hidden   " + FLAG + " flag   " + EMPTY
          + " empty   1-8 mines around")
    print("  " + MINE + " mine   " + HIT + " mine you hit   "
          + WRONG_FLAG + " wrong flag (end of game)")
