"""
Minesweeper - Algorithms and Programming 1 - UFAZ
Team: Zeynalzada Ayxan, Maharramli Anvar, Qurbanli Elton,
      Nuruzada Nihat, Hamzayev Altair
File: game_logic.py
Role: game state, reveal (flood fill), flags, win and loss, one game
"""

import random

from board import (FLAG, HIDDEN, EMPTY, LETTERS,
                   create_board, neighbours, place_mines, compute_numbers)
from interface import display_board, parse_command, show_help


def new_state(rows, cols, nb_mines, seed):
    """Create the dictionary that holds everything about one game.

    Parameters:
        rows (int): number of rows
        cols (int): number of columns
        nb_mines (int): number of mines
        seed (int or None): seed chosen by the player

    Returns:
        dict: the game state
    """
    return {
        "rows": rows,
        "cols": cols,
        "nb_mines": nb_mines,
        "seed": seed,
        "board": create_board(rows, cols),   # what the player sees
        "mines": set(),                      # filled after the first reveal
        "numbers": [],                       # filled after the first reveal
        "revealed": set(),
        "flags": set(),
        "first_move": True,
        "game_over": False,
        "won": False,
        "hit_mine": None,
    }


def start_mines(cell, state):
    """Place the mines and compute the numbers at the first reveal.

    Mines are placed only now, so the first revealed cell is never a mine.

    Parameters:
        cell (tuple): (row, col) of the first revealed cell
        state (dict): the game state (changed in place)

    Returns:
        None
    """
    if state["seed"] is not None:
        random.seed(state["seed"])           # same seed -> same board
    state["mines"] = place_mines(state["rows"], state["cols"],
                                 state["nb_mines"], cell)
    state["numbers"] = compute_numbers(state["mines"],
                                       state["rows"], state["cols"])
    state["first_move"] = False


def reveal(cell, state):
    """Reveal a cell; if it has 0 neighbouring mines, open the whole area.

    The area is opened with a while loop and a list used as a stack
    (no recursion). Flagged cells are never opened.

    Parameters:
        cell (tuple): (row, col) chosen by the player
        state (dict): the game state (changed in place)

    Returns:
        str: an error message, or "" if the move was played
    """
    if cell in state["flags"]:
        return "This cell has a flag. Remove the flag first (F)."
    if cell in state["revealed"]:
        return "This cell is already revealed."
    if state["first_move"]:
        start_mines(cell, state)
    if cell in state["mines"]:
        state["hit_mine"] = cell            # the game is lost
        return ""

    stack = [cell]
    while len(stack) > 0:
        r, c = stack.pop()                  # take the last cell added
        if (r, c) in state["revealed"] or (r, c) in state["flags"]:
            continue                        # already done or protected
        state["revealed"].add((r, c))
        number = state["numbers"][r][c]
        if number == 0:
            state["board"][r][c] = EMPTY
            # a 0 means no neighbour is a mine: push every closed neighbour
            for n in neighbours(r, c, state["rows"], state["cols"]):
                if n not in state["revealed"] and n not in state["flags"]:
                    stack.append(n)
        else:
            state["board"][r][c] = str(number)   # border of the area
    return ""


def toggle_flag(cell, state):
    """Put a flag on a hidden cell, or remove it if it is already there.

    Parameters:
        cell (tuple): (row, col) chosen by the player
        state (dict): the game state (changed in place)

    Returns:
        str: an error message, or "" if the move was played
    """
    if cell in state["revealed"]:
        return "You cannot flag a revealed cell."
    r, c = cell
    if cell in state["flags"]:
        state["flags"].remove(cell)
        state["board"][r][c] = HIDDEN
    else:
        state["flags"].add(cell)
        state["board"][r][c] = FLAG
    return ""


def check_win(state):
    """Check if every safe cell is revealed (flags are not needed).

    Parameters:
        state (dict): the game state

    Returns:
        bool: True if the player has won
    """
    safe_cells = state["rows"] * state["cols"] - state["nb_mines"]
    return len(state["revealed"]) == safe_cells


def check_loss(state):
    """Check if the player revealed a mine.

    Parameters:
        state (dict): the game state

    Returns:
        bool: True if the player has lost
    """
    return state["hit_mine"] is not None


def cell_name(cell):
    """Convert (row, col) into the name shown on screen, e.g. (3, 2) -> 'C4'.

    Parameters:
        cell (tuple): (row, col)

    Returns:
        str: the cell name
    """
    return LETTERS[cell[1]] + str(cell[0] + 1)


def play_game(settings):
    """Play one full game, from the first move to the end.

    Parameters:
        settings (tuple): (rows, cols, nb_mines, seed) from choose_level()

    Returns:
        None
    """
    rows, cols, nb_mines, seed = settings
    state = new_state(rows, cols, nb_mines, seed)
    display_board(state, False)

    while not state["game_over"]:
        text = input("Command (R cell / F cell / D / H / Q): ")
        command, info = parse_command(text, rows, cols)
        message = ""
        if command is None:
            message = info                       # invalid input, ask again
        elif command == "H":
            show_help()
        elif command == "Q":
            print("Game stopped.")
            return
        elif command == "D":
            if state["first_move"]:
                message = "No mines yet: they are placed after your first reveal."
            else:
                print("Debug view (the game continues):")
                display_board(state, True)
        elif command == "R":
            message = reveal(info, state)
        elif command == "F":
            message = toggle_flag(info, state)

        if message != "":
            print(message)                       # the turn is not lost
        elif command in ("R", "F"):
            if check_loss(state):
                state["game_over"] = True
            elif check_win(state):
                state["game_over"] = True
                state["won"] = True
            else:
                display_board(state, False)

    display_board(state, True)                   # full board at the end
    if state["won"]:
        print("Congratulations, you won!")
    else:
        print("Boom! You revealed a mine at " + cell_name(state["hit_mine"])
              + ". You lost.")
