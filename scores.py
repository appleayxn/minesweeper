"""
Minesweeper - Algorithms and Programming 1 - UFAZ
Team: Zeynalzada Ayxan, Maharramli Anvar, Qurbanli Elton,
      Nuruzada Nihat, Hamzayev Altair
File: scores.py
Role: OPTIONAL EXTRA - scoreboard of best times (dictionary), saved in a file
"""

from interface import is_number

SCORES_FILE = "scores.txt"   # created next to main.py on the first win


def board_key(rows, cols, nb_mines):
    """Build the scoreboard key of a board, e.g. '9x9, 10 mines'.

    Parameters:
        rows (int): number of rows
        cols (int): number of columns
        nb_mines (int): number of mines

    Returns:
        str: the key used in the scoreboard dictionary
    """
    return str(rows) + "x" + str(cols) + ", " + str(nb_mines) + " mines"


def load_scores(filename):
    """Read the best times saved in a text file.

    Each line of the file is: key;seconds. The mode "a+" creates the file
    if it does not exist yet, so no error can happen when it is missing.
    Lines that are not well written are ignored.

    Parameters:
        filename (str): name of the file

    Returns:
        dict: key (str) -> best time in seconds (int)
    """
    scores = {}
    file = open(filename, "a+")
    file.seek(0)                      # "a+" starts at the end: go back
    for line in file.read().split("\n"):
        parts = line.split(";")
        if len(parts) == 2 and is_number(parts[1]):
            scores[parts[0]] = int(parts[1])
    file.close()
    return scores


def save_scores(scores, filename):
    """Write all the best times in a text file (one line per board).

    Parameters:
        scores (dict): key (str) -> best time in seconds (int)
        filename (str): name of the file

    Returns:
        None
    """
    file = open(filename, "w")
    for key in scores:
        file.write(key + ";" + str(scores[key]) + "\n")
    file.close()


def update_scores(scores, key, seconds):
    """Store a new time if it is the best one for this board.

    Parameters:
        scores (dict): key -> best time (changed in place)
        key (str): the board key, from board_key()
        seconds (int): time of the game that was just won

    Returns:
        bool: True if it is a new record
    """
    if key not in scores or seconds < scores[key]:
        scores[key] = seconds
        return True
    return False


def show_scores(scores):
    """Print the scoreboard, best time of every board.

    Parameters:
        scores (dict): key -> best time in seconds

    Returns:
        None
    """
    print()
    print("Best times:")
    if len(scores) == 0:
        print("  no game won yet")
    for key in sorted(scores):
        print("  " + key + ": " + str(scores[key]) + " s")
