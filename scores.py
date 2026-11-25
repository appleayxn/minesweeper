"""
Minesweeper - Algorithms and Programming 1 - UFAZ
Team: Zeynalzada Ayxan, Maharramli Anvar, Qurbanli Elton,
      Nuruzada Nihat, Hamzayev Altair
File: scores.py
Role: OPTIONAL EXTRA - best times kept in a dictionary
      (the dictionary lives while the program is running)
"""


def board_key(rows, cols, nb_mines):
    """Make the name of a board for the scoreboard, e.g. '9x9, 10 mines'.

    Parameters:
        rows (int): number of rows
        cols (int): number of columns
        nb_mines (int): number of mines

    Returns:
        str: the key used in the dictionary of best times
    """
    return str(rows) + "x" + str(cols) + ", " + str(nb_mines) + " mines"


def update_scores(scores, key, seconds):
    """Keep the new time if it is the best time for this board.

    Parameters:
        scores (dict): board key -> best time (it is changed)
        key (str): the name of the board
        seconds (int): the time of the game that was won

    Returns:
        bool: True if it is a new record
    """
    if key not in scores:
        scores[key] = seconds
        return True
    if seconds < scores[key]:
        scores[key] = seconds
        return True
    return False


def show_scores(scores):
    """Print the best time of every board.

    Parameters:
        scores (dict): board key -> best time in seconds

    Returns:
        None
    """
    print()
    print("Best times:")
    if len(scores) == 0:
        print("  no game won yet")
    for key in scores:
        print("  " + key + ": " + str(scores[key]) + " s")
