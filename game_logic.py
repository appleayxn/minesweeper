"""
Minesweeper - Algorithms and Programming 1 - UFAZ
Team: Zeynalzada Ayxan, Maharramli Anvar, Qurbanli Elton,
      Nuruzada Nihat, Hamzayev Altair
File: game_logic.py
Role: game state, reveal (flood fill), flags, win and loss, one game
"""

import random
import time

from board import FLAG, HIDDEN, EMPTY, LETTERS
from board import create_board, neighbours, place_mines, compute_numbers
from board import place_mines_safe
from interface import display_board, parse_command, show_help


def new_state(rows, cols, nb_mines, seed):
    """Create the dictionary that contains everything about one game.

    Parameters:
        rows (int): number of rows
        cols (int): number of columns
        nb_mines (int): number of mines
        seed (int): the seed of the game

    Returns:
        dict: the game state
    """
    state = {}
    state["rows"] = rows
    state["cols"] = cols
    state["nb_mines"] = nb_mines
    state["seed"] = seed
    state["board"] = create_board(rows, cols)   # what the player sees
    state["mines"] = set()                      # filled at the first reveal
    state["numbers"] = []                       # filled at the first reveal
    state["revealed"] = set()                   # cells already revealed
    state["flags"] = set()                      # cells with a flag
    state["first_move"] = True
    state["game_over"] = False
    state["won"] = False
    state["hit_mine"] = None                    # the mine that exploded
    state["safe_start"] = False                 # extra: safer first move
    state["colors"] = False                     # extra: colours in the terminal
    return state


def start_mines(cell, state):
    """Place the mines and compute the numbers, at the first reveal.

    Because the mines are placed only now, the first cell is never a mine.

    Parameters:
        cell (tuple): (row, col) of the first revealed cell
        state (dict): the game state (it is changed)

    Returns:
        None
    """
    random.seed(state["seed"])        # same seed -> same mines
    if state["safe_start"] == True:
        # extra: no mine on the cell and on its 8 neighbours
        state["mines"] = place_mines_safe(state["rows"], state["cols"],
                                          state["nb_mines"], cell)
    else:
        state["mines"] = place_mines(state["rows"], state["cols"],
                                     state["nb_mines"], cell)
    state["numbers"] = compute_numbers(state["mines"],
                                       state["rows"], state["cols"])
    state["first_move"] = False


def reveal(cell, state):
    """Reveal a cell. If it has 0 mines around, reveal the whole area.

    The area is opened with a while loop and a list used as a stack
    (no recursion). A cell with a flag is never opened.

    Parameters:
        cell (tuple): (row, col) chosen by the player
        state (dict): the game state (it is changed)

    Returns:
        str: an error message, or "" if the move was played
    """
    if cell in state["flags"]:
        return "This cell has a flag. Remove the flag first (F)."
    if cell in state["revealed"]:
        return "This cell is already revealed."

    if state["first_move"] == True:
        start_mines(cell, state)

    if cell in state["mines"]:
        state["hit_mine"] = cell          # the player loses
        return ""

    # ----- flood fill with a stack -----
    stack = []
    stack.append(cell)
    while len(stack) > 0:
        current = stack.pop()             # take the last cell of the list
        r = current[0]
        c = current[1]

        already_revealed = current in state["revealed"]
        has_flag = current in state["flags"]

        if already_revealed == False and has_flag == False:
            state["revealed"].add(current)
            number = state["numbers"][r][c]

            if number == 0:
                # 0 mines around: all the neighbours are safe
                state["board"][r][c] = EMPTY
                around = neighbours(r, c, state["rows"], state["cols"])
                for n in around:
                    if n not in state["revealed"] and n not in state["flags"]:
                        stack.append(n)       # open it later
            else:
                # a number: we stop here
                state["board"][r][c] = str(number)
    return ""


def toggle_flag(cell, state):
    """Put a flag on a hidden cell, or remove the flag if there is one.

    Parameters:
        cell (tuple): (row, col) chosen by the player
        state (dict): the game state (it is changed)

    Returns:
        str: an error message, or "" if the move was played
    """
    if cell in state["revealed"]:
        return "You cannot flag a revealed cell."

    r = cell[0]
    c = cell[1]
    if cell in state["flags"]:
        state["flags"].remove(cell)       # remove the flag
        state["board"][r][c] = HIDDEN
    else:
        state["flags"].add(cell)          # put a flag
        state["board"][r][c] = FLAG
    return ""


def check_win(state):
    """Check if all the cells without a mine are revealed.

    Flags are not needed to win.

    Parameters:
        state (dict): the game state

    Returns:
        bool: True if the player has won
    """
    total_cells = state["rows"] * state["cols"]
    safe_cells = total_cells - state["nb_mines"]
    revealed_cells = len(state["revealed"])
    if revealed_cells == safe_cells:
        return True
    return False


def check_loss(state):
    """Check if the player revealed a mine.

    Parameters:
        state (dict): the game state

    Returns:
        bool: True if the player has lost
    """
    if state["hit_mine"] == None:
        return False
    return True


def find_hint(state):
    """OPTIONAL EXTRA - find a safe hidden cell to help the player.

    First we look for a safe cell next to a revealed cell.
    If there is none, we take any safe hidden cell.

    Parameters:
        state (dict): the game state (the mines are already placed)

    Returns:
        tuple: (row, col) of a safe hidden cell, or None
    """
    # first try: a safe hidden cell next to the revealed area
    for r in range(state["rows"]):
        for c in range(state["cols"]):
            cell = (r, c)
            is_free = True
            if cell in state["mines"]:
                is_free = False
            if cell in state["revealed"]:
                is_free = False
            if cell in state["flags"]:
                is_free = False
            if is_free == True:
                around = neighbours(r, c, state["rows"], state["cols"])
                for n in around:
                    if n in state["revealed"]:
                        return cell

    # second try: any safe hidden cell
    for r in range(state["rows"]):
        for c in range(state["cols"]):
            cell = (r, c)
            if cell not in state["mines"]:
                if cell not in state["revealed"]:
                    if cell not in state["flags"]:
                        return cell
    return None


def cell_name(cell):
    """Change (row, col) into the name shown on screen: (3, 2) -> 'C4'.

    Parameters:
        cell (tuple): (row, col)

    Returns:
        str: the name of the cell
    """
    row = cell[0]
    col = cell[1]
    return LETTERS[col] + str(row + 1)


def play_game(settings, use_colors):
    """Play one full game, from the first move to the end.

    Parameters:
        settings (tuple): (rows, cols, nb_mines, seed, safe_start)
        use_colors (bool): True to show the board in colour (extra)

    Returns:
        int: the time in seconds if the game is won, otherwise None
    """
    rows = settings[0]
    cols = settings[1]
    nb_mines = settings[2]
    seed = settings[3]
    safe_start = settings[4]

    state = new_state(rows, cols, nb_mines, seed)
    state["safe_start"] = safe_start
    state["colors"] = use_colors
    if safe_start == True:
        print("Safe start: there is no mine around your first cell.")
    start_time = time.time()                  # extra: timer
    display_board(state, False)

    while state["game_over"] == False:
        text = input("Command (R cell / F cell / D / H / Q): ")
        result = parse_command(text, rows, cols)
        command = result[0]
        info = result[1]
        message = ""

        if command == None:
            message = info                    # wrong input: ask again
        elif command == "H":
            show_help()
        elif command == "Q":
            print("Game stopped.")
            return None
        elif command == "D":
            if state["first_move"] == True:
                message = "No mines yet: they are placed after your first reveal."
            else:
                print("Debug view (the game continues):")
                display_board(state, True)
        elif command == "HINT":               # extra: hint
            if state["first_move"] == True:
                message = "Reveal a first cell before asking for a hint."
            else:
                hint = find_hint(state)
                print("Hint: " + cell_name(hint) + " is safe.")
        elif command == "R":
            message = reveal(info, state)
        elif command == "F":
            message = toggle_flag(info, state)

        if message != "":
            print(message)                    # the turn is not lost
        elif command == "R" or command == "F":
            if check_loss(state) == True:
                state["game_over"] = True
            elif check_win(state) == True:
                state["game_over"] = True
                state["won"] = True
            else:
                display_board(state, False)

    # ----- end of the game: show the full board -----
    display_board(state, True)
    if state["won"] == True:
        seconds = int(time.time() - start_time)
        print("Congratulations, you won! Time: " + str(seconds) + " s")
        return seconds
    print("Boom! You revealed a mine at " + cell_name(state["hit_mine"])
          + ". You lost.")
    return None
